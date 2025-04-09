from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def style_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Studio", callback_data="style_studio")],
        [InlineKeyboardButton(text="🧙 Fantasy", callback_data="style_fantasy")],
        [InlineKeyboardButton(text="🎥 Cinematic", callback_data="style_cinematic")],
        [InlineKeyboardButton(text="📝 Custom prompt", callback_data="style_custom")],
    ])
