import aiosqlite
from asyncio import create_task

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from PIL import Image
from keyboards.main_menu import get_back_button
from image_utils import crop_center, resize_image, determine_target_size
from database import (
    get_payment_status,
    count_photos,
    exists_photo,
    save_photo,            # now just records user_id, file_id, unique_id
)
from utils.avatar import generate_avatar_task

router = Router()

UPLOAD_PROGRESS_KEY = "upload_message_id"
SUPPORTED_FILE_TYPES = ['image/jpeg', 'image/png']


@router.message(F.text == "📤 Upload photos")
async def handle_upload_click(message: Message, state: FSMContext):
    await message.answer("🚀🚀🚀", reply_markup= get_back_button())

    """Starts the upload session by sending a progress message."""
    msg = await message.answer("📤 Upload your photos. Uploaded: 0/10")
    await state.update_data(**{UPLOAD_PROGRESS_KEY: msg.message_id})


@router.message(F.video)
async def reject_video(message: Message):
    """Reject any video files."""
    await message.answer("❗ Video uploads are not supported. Please send photos only.")


@router.message(F.document)
async def reject_non_photo(message: Message):
    """Reject non-image documents by MIME type."""
    if message.document.mime_type not in SUPPORTED_FILE_TYPES:
        await message.answer(
            f"❗ Unsupported file type: {message.document.mime_type}. Please upload JPEG or PNG."
        )


@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    """Handle an incoming photo: dedupe, in‐memory process, record in DB, update progress."""
    user_id = message.chat.id

    # 1) Ensure user has paid
    if await get_payment_status(user_id) != 'paid':
        return await message.answer("❗ Please pay before uploading photos.")

    # 2) Enforce 10‐photo limit
    current_count = await count_photos(user_id)
    if current_count >= 10:
        return await message.answer("✅ You already uploaded 10 photos.")

    # 3) Select the largest size and check duplicate
    largest = max(message.photo, key=lambda p: p.file_size)
    file_id   = largest.file_id
    uniq_id   = largest.file_unique_id

    if await exists_photo(user_id, uniq_id):
        return await message.answer("⛔ This photo is already uploaded.")

    # 4) Download + process image purely in memory
    try:
        # download raw bytes
        f   = await message.bot.get_file(file_id)
        bio = await message.bot.download_file(f.file_path)

        # open and normalize
        img = Image.open(bio)
        if img.mode != "RGB":
            img = img.convert("RGB")

        # crop & resize
        tgt_size, tgt_aspect = determine_target_size(img)
        img = crop_center(img, tgt_aspect)
        img = resize_image(img, tgt_size)

        # 5) Record the upload in the DB only (no disk I/O)
        #    `file_path` can be left empty since we no longer store it locally
        await save_photo(user_id, file_id, uniq_id)

    except Exception as e:
        print("❌ Error processing photo:", e)
        return await message.answer("❌ Error while processing photo. Try again later.")

    # 6) Update the upload‐progress message
    updated_count = await count_photos(user_id)
    data          = await state.get_data()
    prog_msg_id   = data.get(UPLOAD_PROGRESS_KEY)

    if prog_msg_id:
        try:
            if updated_count < 10:
                await message.bot.edit_message_text(
                    chat_id=user_id,
                    message_id=prog_msg_id,
                    text=f"📤 Uploaded: {updated_count}/10"
                )
            else:
                # exactly 10 photos now
                await message.bot.edit_message_text(
                    chat_id=user_id,
                    message_id=prog_msg_id,
                    text="✅ All photos uploaded! Generating your avatar…"
                )
                await message.answer("🤖 Your avatar is being generated… Please wait ⏳")

                # launch the one‐time avatar generation
                create_task(generate_avatar_task(user_id, message.bot))

        except Exception as e:
            print("⚠️ Error updating progress message:", e)


@router.callback_query(F.data == "start_over")
async def handle_start_over(callback: CallbackQuery, state: FSMContext):
    """Clears all uploads and resets payment, but does not touch generation credits."""
    user_id = callback.from_user.id

    # 1) Remove all records of this user's photos
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("DELETE FROM user_photo WHERE user_id = ?", (user_id,))
        # 2) Force them to pay again for the next 10-photo→avatar cycle
        await db.execute(
            "UPDATE payment SET status = 'waiting' WHERE telegram_user_id = ?",
            (user_id,)
        )
        await db.commit()

    await callback.answer()

    # 3) Start a fresh upload progress message
    msg = await callback.message.answer("📤 Upload your photos. Uploaded: 0/10")
    await state.update_data(**{UPLOAD_PROGRESS_KEY: msg.message_id})


async def safe_edit(bot, chat_id, message_id, new_text, new_markup=None):
    try:
        # Получаем текущее сообщение
        current = await bot.get_message(chat_id, message_id)
        
        # Проверка изменения текста и разметки
        if current.text != new_text or current.reply_markup != new_markup:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, reply_markup=new_markup)
        else:
            print("✅ No changes detected, skipping update.")
    
    except Exception as e:
        print(f"⚠️ Error updating progress message: {e}")


