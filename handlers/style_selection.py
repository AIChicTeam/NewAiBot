from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import decrease_credits, get_credits

router = Router()

STYLES = [
    "🎨 Anime", "🧙 Fantasy", "👗 Fashion", "🎬 Cinematic",
    "🕶 Noir", "🧑‍🚀 Sci-Fi", "✍️ Sketch", "🧚‍♀️ Fairytale"
]

# 🔄 FSM
class PromptState(StatesGroup):
    waiting_for_custom_prompt = State()

# ✅ Кнопки "Выбрать стиль / Ввести промпт"
@router.callback_query(F.data == "after_avatar_ready")
async def show_generation_options(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎨 Choose Style", callback_data="select_style")
    kb.button(text="📝 Enter Custom Prompt", callback_data="custom_prompt")
    kb.adjust(1)
    await callback.message.answer("✅ Your AI avatar is ready! Click below to choose a style or enter a custom prompt.", reply_markup=kb.as_markup())
    await callback.answer()

# 🎨 Клавиатура выбора стиля
@router.callback_query(F.data == "select_style")
async def select_style(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for style in STYLES:
        kb.button(text=style, callback_data=f"style_{style}")
    kb.button(text="💬 Custom Prompt", callback_data="custom_prompt")
    kb.adjust(2)
    await callback.message.answer("🎨 Choose a style or enter a custom prompt:", reply_markup=kb.as_markup())
    await callback.answer()

# 🧠 Генерация по стилю
@router.callback_query(F.data.startswith("style_"))
async def generate_with_style(callback: CallbackQuery):
    style = callback.data.replace("style_", "")
    user_id = callback.from_user.id

    if not await decrease_credits(user_id):
        await callback.message.answer("⚠️ You’ve used all 100 generations. Please pay again to continue.")
        await callback.answer()
        return

    await callback.message.answer(f"🧠 Generating image with style: {style}...\n(placeholder, real generation will be here)")
    await callback.message.answer(f"🧮 You currently have {await get_credits(user_id)} generation(s) remaining.")
    await callback.answer()

# ✍️ Пользователь выбрал кастомный промпт
@router.callback_query(F.data == "custom_prompt")
async def ask_for_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✍️ Send me your custom prompt:")
    await state.set_state(PromptState.waiting_for_custom_prompt)
    await callback.answer()

# 📥 Получаем текст промпта
@router.message(PromptState.waiting_for_custom_prompt)
async def handle_prompt(message: Message, state: FSMContext):
    prompt = message.text
    user_id = message.from_user.id

    if not await decrease_credits(user_id):
        await message.answer("⚠️ You’ve used all 100 generations. Please pay again to continue.")
        return

    await message.answer(f"🧠 Generating with your prompt: {prompt}\n(placeholder, real generation will be here)")
    await message.answer(f"🧮 You currently have {await get_credits(user_id)} generation(s) remaining.")
    await state.clear()
