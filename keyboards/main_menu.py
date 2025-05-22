from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_main_menu(can_select_style: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="📤 Upload photos"),
            KeyboardButton(text="🧮 Balance"),
        ],
        [
            KeyboardButton(text="💳 Pay now"),
            KeyboardButton(text="♻️ Start over"),
        ],
        [
            KeyboardButton(text = "More..."),            
        ],
    ]

    if can_select_style:
        keyboard.append([
            KeyboardButton(text="🎨 Select Style"),
        ])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_back_button() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="↩Back")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Также оставим функцию оплаты, как у тебя:
def generate_payment_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="💰 Pay with Crypto",
            url=f"http://localhost:8000/create-crypto-invoice?telegram_user_id={user_id}"
        )
    ]])
