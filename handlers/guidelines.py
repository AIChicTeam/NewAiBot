from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "how_it_works")
async def how_it_works_handler(callback: CallbackQuery):
    text = (
        "📸 *How it works?* — Your AI Avatar Journey Starts Here!\n\n"
        "Welcome! Here's a quick guide on how to create stunning AI-generated avatars:\n\n"
        "1️⃣ *Upload Your Photos*\n"
        "   ┗ Upload *10 clear selfies* — ideally with different backgrounds, angles, and expressions.\n"
        "   📌 Tip: Avoid heavy filters or group shots.\n\n"
        "2️⃣ *Select a Style* 🎨\n"
        "   ┗ Choose from various creative themes (Fantasy, Cyberpunk, Professional, etc).\n"
        "   ✨ You can change styles later if allowed.\n\n"
        "3️⃣ *Make a Secure Payment* 💳\n"
        "   ┗ Pay safely using cryptocurrency. We use trusted gateways and generate one-time links.\n\n"
        "4️⃣ *Receive Your Avatars* 🖼️\n"
        "   ┗ Processing takes just a few minutes.\n"
        "   🎁 You'll receive *unique, high-quality avatars* ready to use on any platform!\n\n"
        "🔒 *Privacy First*: Your photos are processed securely and deleted afterwards.\n"
        "❓ *Need help?* Send /help anytime."
    )

    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()
