from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import plan_keyboard, word_limit_buttons
from database.users import UserManager
from database.db import db
from handlers.start import main_menu

router = Router()

class PaymentState(StatesGroup):
    waiting_plan = State()
    waiting_screenshot = State()

@router.callback_query(F.data == "premium_info")
async def premium_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user = await UserManager.get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Restart with /start")
        return
    country = user.get('country', 'global')
    await state.update_data(country=country)
    await state.set_state(PaymentState.waiting_plan)
    await callback.message.edit_text(
        "⭐ *Premium Plans*\n\n• 10-15 assignments/day\n• PDF + DOCX export\n• Word limit control (100-1500 words)\n• Priority generation\n\nSelect your plan:",
        reply_markup=plan_keyboard(country),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "set_word_limit")
async def set_word_limit_callback(callback: CallbackQuery):
    user = await UserManager.get_user(callback.from_user.id)
    if not user or not user.get('is_premium'):
        await callback.answer("Only premium users can set word limit.")
        return
    current_limit = user.get('word_limit', 1000)
    await callback.message.edit_text(
        "📝 *Set your assignment word limit*\n\nChoose how many words you want per assignment (lower = faster & cheaper):",
        reply_markup=word_limit_buttons(current_limit),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("wordlimit_"))
async def change_word_limit(callback: CallbackQuery):
    user_id = callback.from_user.id
    new_limit = int(callback.data.split("_")[1])
    await db.execute("UPDATE users SET word_limit = ? WHERE user_id = ?", (new_limit, user_id))
    await callback.answer(f"Word limit set to {new_limit} words!")
    await callback.message.delete()
    user = await UserManager.get_user(user_id)
    is_premium = user.get('is_premium', False)
    await callback.message.answer("Main menu:", reply_markup=main_menu(is_premium))