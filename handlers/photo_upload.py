import os
import io
import shutil
from asyncio import create_task  
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from image_utils import crop_center, resize_image, determine_target_size
from database import get_payment_status, count_photos, exists_photo, save_photo
from PIL import Image
import aiosqlite

from utils.avatar import generate_avatar_task  

router = Router()
UPLOAD_PROGRESS_KEY = "upload_message_id"


@router.callback_query(F.data == "upload_photos")
async def handle_upload_click(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    message = await callback.message.answer("📤 Upload your photos. Uploaded: 0/10")
    await state.update_data(**{UPLOAD_PROGRESS_KEY: message.message_id})


@router.message(F.video)
async def reject_video(message: Message):
    await message.answer("❗ Video uploads are not supported. Please send photos only.")


@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    user_id = message.chat.id

    # Проверка оплаты
    payment_status = await get_payment_status(user_id)
    if payment_status != 'paid':
        await message.answer("❗ Please pay before uploading photos.")
        return

    # Проверка лимита
    current_count = await count_photos(user_id)
    if current_count >= 10:
        await message.answer("✅ You already uploaded 10 photos.")
        return

    # Дубли
    largest_photo = max(message.photo, key=lambda p: p.file_size)
    file_id = largest_photo.file_id
    unique_id = largest_photo.file_unique_id

    if await exists_photo(user_id, unique_id):
        await message.answer("⛔ This photo is already uploaded.")
        return

    # Обработка
    try:
        file = await message.bot.get_file(file_id)
        downloaded = await message.bot.download_file(file.file_path)

        image = Image.open(downloaded)
        if image.mode != "RGB":
            image = image.convert("RGB")

        target_size, target_aspect = determine_target_size(image)
        image = crop_center(image, target_aspect)
        image = resize_image(image, target_size)

        os.makedirs(f"user_photos/{user_id}", exist_ok=True)
        save_path = f"user_photos/{user_id}/{unique_id}.jpg"
        image.save(save_path, format="JPEG", quality=95)

        await save_photo(user_id, file_id, unique_id, save_path)

        updated_count = await count_photos(user_id)

        # Получаем ID сообщения с прогрессом
        data = await state.get_data()
        upload_msg_id = data.get(UPLOAD_PROGRESS_KEY)

        if upload_msg_id:
            try:
                if updated_count < 10:
                    await message.bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=upload_msg_id,
                        text=f"📤 Uploaded: {updated_count}/10"
                    )
                else:
                    await message.bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=upload_msg_id,
                        text="✅ All photos uploaded! Thank you!"
                    )
                    create_task(generate_avatar_task(user_id, message.bot))

            except Exception as e:
                print("⚠️ Error updating progress message:", e)

    except Exception as e:
        await message.answer("❌ Error while processing photo.")
        print("❌", e)


@router.callback_query(F.data == "start_over")
async def handle_start_over(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # Удаление из БД
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("DELETE FROM user_photo WHERE user_id = ?", (user_id,))
        await db.commit()

    # Удаление файлов
    folder = f"user_photos/{user_id}"
    if os.path.exists(folder):
        shutil.rmtree(folder)

    await callback.answer()

    # Автоматически отправляем новое сообщение прогресса
    msg = await callback.message.answer("📤 Upload your photos. Uploaded: 0/10")
    await state.update_data(upload_message_id=msg.message_id)


async def safe_edit(bot, chat_id, message_id, new_text):
    try:
        current = await bot.get_message(chat_id, message_id)
        if current.text != new_text:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text)
    except Exception as e:
        print("⚠️ Error updating progress message:", e)
