from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.premium import PaymentState
from database.users import UserManager
from database.payments import PaymentManager
from config import (
    ADMIN_IDS, UPI_ID, USD_WALLET,
    PRICE_1M_INR, PRICE_3M_INR, PRICE_1M_USD, PRICE_3M_USD
)
from keyboards.inline import admin_payment_buttons

router = Router()

@router.callback_query(PaymentState.waiting_plan, F.data.startswith("plan_"))
async def process_plan(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    plan = callback.data
    user_data = await state.get_data()
    country = user_data.get('country')
    
    if "1m" in plan:
        plan_type = "1_month"
        if "inr" in plan:
            amount = str(PRICE_1M_INR)
            currency = "INR"
            payment_method = "UPI"
            details = f"Send ₹{amount} to UPI ID: {UPI_ID}"
        else:
            amount = str(PRICE_1M_USD)
            currency = "USD"
            payment_method = "CRYPTO"
            details = f"Send ${amount} to wallet: {USD_WALLET}"
    else:
        plan_type = "3_months"
        if "inr" in plan:
            amount = str(PRICE_3M_INR)
            currency = "INR"
            payment_method = "UPI"
            details = f"Send ₹{amount} to UPI ID: {UPI_ID}"
        else:
            amount = str(PRICE_3M_USD)
            currency = "USD"
            payment_method = "CRYPTO"
            details = f"Send ${amount} to wallet: {USD_WALLET}"
    
    await state.update_data(
        plan_type=plan_type,
        amount=amount,
        currency=currency,
        payment_method=payment_method
    )
    await callback.message.edit_text(
        f"💳 *Payment Instructions*\n\n{details}\n\nAfter payment, send screenshot of transaction here.",
        parse_mode="Markdown"
    )
    await state.set_state(PaymentState.waiting_screenshot)

@router.message(PaymentState.waiting_screenshot, F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_id = photo.file_id
    data = await state.get_data()
    user_id = message.from_user.id
    
    await PaymentManager.create_payment(
        user_id=user_id,
        plan_type=data['plan_type'],
        amount=data['amount'],
        currency=data['currency'],
        screenshot_file_id=file_id,
        payment_method=data['payment_method']
    )
    
    pending = await PaymentManager.get_pending_payments()
    payment_id = pending[-1]['id'] if pending else None
    
    await message.answer("✅ Screenshot received! Admin will verify shortly.")
    
    user = message.from_user
    username = f"@{user.username}" if user.username else f"ID: {user.id}"
    caption = (
        f"🧾 *New Payment Request*\n\n"
        f"👤 User: {username}\n"
        f"🆔 User ID: {user.id}\n"
        f"📅 Plan: {data['plan_type']}\n"
        f"💰 Amount: {data['amount']} {data['currency']}\n"
        f"💳 Method: {data['payment_method']}\n"
        f"🆔 Payment ID: {payment_id}\n\n"
        f"Use buttons below."
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=caption,
                reply_markup=admin_payment_buttons(payment_id),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Failed to forward to admin {admin_id}: {e}")
    
    from handlers.start import main_menu
    user_obj = await UserManager.get_user(user_id)
    is_premium = user_obj.get('is_premium', False) if user_obj else False
    await message.answer("Back to menu:", reply_markup=main_menu(is_premium))
    await state.clear()