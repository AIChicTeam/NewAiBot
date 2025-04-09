from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📸 How it works?", callback_data="how_it_works"),
            InlineKeyboardButton(text="📤 Upload photos", callback_data="upload_photos")
        ],
        [
            InlineKeyboardButton(text="🎁 Invite friends", callback_data="invite_friends"),
            InlineKeyboardButton(text="🛟 Support", url="https://t.me/your_support_bot")
        ],
        [
            InlineKeyboardButton(text="💳 Pay now", callback_data="pay"),
            InlineKeyboardButton(text="🧮 Balance", callback_data="check_balance")
        ],
        [
            InlineKeyboardButton(text="♻️ Start over", callback_data="start_over")
        ]
    ]
)



def generate_payment_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💳 Pay now",
            url=f"http://localhost:8000/create-checkout-session?telegram_user_id={user_id}"
        )]
    ])