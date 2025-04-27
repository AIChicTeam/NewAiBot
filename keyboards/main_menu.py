from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu(can_select_style: bool = False) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="📸 How it works?", callback_data="how_it_works"),
            InlineKeyboardButton(text="📤 Upload photos", callback_data="upload_photos"),
        ],
        [
            InlineKeyboardButton(text="🎁 Invite friends", callback_data="invite_friends"),
            InlineKeyboardButton(text="🛟 Support", url="https://t.me/your_support_bot"),
        ],
        [
            InlineKeyboardButton(text="💳 Pay now", callback_data="pay"),
            InlineKeyboardButton(text="🧮 Balance", callback_data="check_balance"),
        ],
        [
            InlineKeyboardButton(text="♻️ Start over", callback_data="start_over"),
        ],
    ]

    if can_select_style:
        keyboard.append([
            InlineKeyboardButton(text="🎨 Select Style", callback_data="select_style"),
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)



# Также оставим функцию оплаты, как у тебя:
def generate_payment_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="💰 Pay with Crypto",
            url=f"http://localhost:8000/create-crypto-invoice?telegram_user_id={user_id}"
        )
    ]])
