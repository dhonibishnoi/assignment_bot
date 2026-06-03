from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards.inline import country_keyboard, main_menu
from database.users import UserManager
from utils.expiry import check_and_expire_premium

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    await check_and_expire_premium()
    user = await UserManager.get_user(user_id)
    if not user:
        await message.answer(
            "📚 *Assignment Bot*\n\nWelcome! I generate human-like academic assignments.\n\n• Free: 2 assignments total\n• Premium: 10-15/day, PDF/DOCX, word limit control\n\nSelect your country:",
            reply_markup=country_keyboard(),
            parse_mode="Markdown"
        )
    else:
        is_premium = user.get('is_premium', False)
        await message.answer(
            f"Welcome back! You are {'Premium' if is_premium else 'Free'} user.\n\nUse the menu below:",
            reply_markup=main_menu(is_premium)
        )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.answer()
    user = await UserManager.get_user(callback.from_user.id)
    is_premium = user.get('is_premium', False) if user else False
    await callback.message.edit_text("Main menu:", reply_markup=main_menu(is_premium))

@router.callback_query(F.data == "country_india")
async def set_country_india(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    username = callback.from_user.username or ""
    first_name = callback.from_user.first_name or ""
    user = await UserManager.get_user(user_id)
    if not user:
        await UserManager.create_user(user_id, username, first_name, "india")
    else:
        await UserManager.update_country(user_id, "india")
    await callback.message.edit_text("Country set to India. You can now use the bot.")
    await back_to_menu(callback)

@router.callback_query(F.data == "country_global")
async def set_country_global(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    username = callback.from_user.username or ""
    first_name = callback.from_user.first_name or ""
    user = await UserManager.get_user(user_id)
    if not user:
        await UserManager.create_user(user_id, username, first_name, "global")
    else:
        await UserManager.update_country(user_id, "global")
    await callback.message.edit_text("Country set to Global. You can now use the bot.")
    await back_to_menu(callback)