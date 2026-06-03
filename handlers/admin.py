from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from database.payments import PaymentManager
from database.users import UserManager
from database.db import db
from keyboards.inline import admin_payment_buttons, admin_menu_buttons
import csv, io, asyncio
from datetime import datetime, timedelta

router = Router()

class BroadcastState(StatesGroup):
    waiting_message = State()

async def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("? Admin only.")
        return
    pending = await PaymentManager.get_pending_payments()
    total_users = await db.fetch_one("SELECT COUNT(*) as count FROM users")
    premium_users = await db.fetch_one("SELECT COUNT(*) as count FROM users WHERE is_premium=1")
    text = (f"?? *Admin Panel*\n\n?? Pending: {len(pending)}\n?? Total: {total_users['count']}\n? Premium: {premium_users['count']}\n\nUse buttons below:")
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=admin_menu_buttons())

@router.callback_query(F.data == "admin_pending")
async def admin_pending_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Unauthorized")
        return
    pending = await PaymentManager.get_pending_payments()
    if not pending:
        await callback.message.answer("[OK] No pending payments.")
        await callback.answer()
        return
    for payment in pending:
        user = await UserManager.get_user(payment['user_id'])
        username = user.get('username', 'Unknown') if user else 'Unknown'
        text = (f"?? *Payment #{payment['id']}*\n?? {username} (ID: {payment['user_id']})\n?? {payment['plan_type']}\n?? {payment['amount']} {payment['currency']}")
        await callback.message.answer(text, reply_markup=admin_payment_buttons(payment['id']), parse_mode=ParseMode.MARKDOWN)
    await callback.answer()

@router.callback_query(F.data == "admin_premium_users")
async def admin_premium_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Unauthorized")
        return
    users = await db.fetch_all("SELECT user_id, username, premium_plan, premium_expiry FROM users WHERE is_premium=1")
    if not users:
        await callback.message.answer("No premium users.")
        await callback.answer()
        return
    text = "*? Premium Users:*\n\n"
    for u in users:
        text += f"?? {u['user_id']} | @{u['username'] or 'N/A'}\n   Plan: {u['premium_plan']}\n   Expiry: {u['premium_expiry']}\n\n"
    await callback.message.answer(text[:4000], parse_mode=ParseMode.MARKDOWN)
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Unauthorized")
        return
    total_users = await db.fetch_one("SELECT COUNT(*) as count FROM users")
    premium_users = await db.fetch_one("SELECT COUNT(*) as count FROM users WHERE is_premium=1")
    free_users = total_users['count'] - premium_users['count']
    total_payments = await db.fetch_one("SELECT COUNT(*) as count FROM payments")
    approved = await db.fetch_one("SELECT COUNT(*) as count FROM payments WHERE status='approved'")
    inr = await db.fetch_one("SELECT SUM(CAST(amount AS REAL)) as total FROM payments WHERE currency='INR' AND status='approved'")
    usd = await db.fetch_one("SELECT SUM(CAST(amount AS REAL)) as total FROM payments WHERE currency='USD' AND status='approved'")
    text = (f"?? *Stats*\n\n?? Total: {total_users['count']}\n? Premium: {premium_users['count']}\n?? Free: {free_users}\n?? Payments: {total_payments['count']} (Approved: {approved['count']})\n?? INR: ?{inr['total'] or 0}\n?? USD: ${usd['total'] or 0}")
    await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN)
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_prompt(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Unauthorized")
        return
    await callback.message.answer("?? Send the broadcast message (text). To cancel, send /cancel")
    await state.set_state(BroadcastState.waiting_message)
    await callback.answer()

@router.message(BroadcastState.waiting_message)
async def send_broadcast(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("? Admin only.")
        return
    broadcast_text = message.text
    users = await db.fetch_all("SELECT user_id FROM users")
    if not users:
        await message.answer("No users found.")
        await state.clear()
        return
    success = 0
    fail = 0
    await message.answer("? Broadcasting...")
    for user in users:
        try:
            await message.bot.send_message(user['user_id'], f"?? *Announcement*\n\n{broadcast_text}", parse_mode=ParseMode.MARKDOWN)
            success += 1
        except:
            fail += 1
        await asyncio.sleep(0.05)
    await message.answer(f"[OK] Done: {success} sent, {fail} failed.")
    await state.clear()

@router.callback_query(F.data == "admin_export")
async def admin_export_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Unauthorized")
        return
    users = await db.fetch_all("SELECT user_id, username, first_name, country, is_premium, premium_plan, premium_expiry, created_at FROM users")
    if not users:
        await callback.message.answer("No users.")
        await callback.answer()
        return
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["User ID", "Username", "First Name", "Country", "Premium", "Plan", "Expiry", "Created At"])
    for u in users:
        writer.writerow([u['user_id'], u['username'] or "", u['first_name'] or "", u['country'] or "", u['is_premium'], u['premium_plan'] or "", u['premium_expiry'] or "", u['created_at']])
    output.seek(0)
    await callback.message.answer_document(io.BytesIO(output.getvalue().encode('utf-8')), filename=f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    output.close()
    await callback.answer()

@router.callback_query(F.data == "admin_activate")
async def admin_activate_prompt(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Unauthorized")
        return
    await callback.message.answer("Usage: `/activate <user_id> <days>`\nExample: `/activate 123456789 30`")
    await callback.answer()

@router.callback_query(F.data == "admin_deactivate")
async def admin_deactivate_prompt(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Unauthorized")
        return
    await callback.message.answer("Usage: `/deactivate <user_id>`\nExample: `/deactivate 123456789`")
    await callback.answer()

@router.message(Command("activate"))
async def activate_premium_cmd(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("? Admin only.")
        return
    args = message.text.split()
    if len(args) < 3:
        await message.answer("Usage: `/activate <user_id> <days>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        user_id = int(args[1])
        days = int(args[2])
    except:
        await message.answer("Invalid user_id or days.")
        return
    user = await UserManager.get_user(user_id)
    if not user:
        await message.answer(f"User {user_id} not found. Ask them to /start first.")
        return
    plan = f"manual_{days}"
    await UserManager.activate_premium(user_id, plan, days)
    await message.answer(f"[OK] Premium activated for {user_id} for {days} days.")
    await message.bot.send_message(user_id, f"?? Admin activated your premium for {days} days! Enjoy.")

@router.message(Command("deactivate"))
async def deactivate_premium_cmd(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("? Admin only.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: `/deactivate <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        user_id = int(args[1])
    except:
        await message.answer("Invalid user_id.")
        return
    user = await UserManager.get_user(user_id)
    if not user or not user.get('is_premium'):
        await message.answer(f"User {user_id} is not premium.")
        return
    await UserManager.remove_premium(user_id)
    await message.answer(f"[FAIL] Premium removed for {user_id}.")
    await message.bot.send_message(user_id, "? Your premium subscription was removed by admin.")

@router.callback_query(F.data.startswith("approve_"))
async def approve_payment(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Unauthorized")
        return
    payment_id = int(callback.data.split("_")[1])
    payment = await PaymentManager.get_payment(payment_id)
    if not payment or payment['status'] != 'pending':
        await callback.answer("Payment not found or already processed")
        return
    await PaymentManager.approve_payment(payment_id, callback.from_user.id)
    expiry_days = 30 if payment['plan_type'] == '1_month' else 90
    await UserManager.activate_premium(payment['user_id'], payment['plan_type'], expiry_days)
    await callback.bot.send_message(payment['user_id'], "?? *Premium activated!* Enjoy unlimited assignments, PDF/DOCX exports.", parse_mode=ParseMode.MARKDOWN)
    await callback.message.edit_text(f"[OK] Payment #{payment_id} approved. Premium activated.")
    await callback.answer()

@router.callback_query(F.data.startswith("reject_"))
async def reject_payment(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Unauthorized")
        return
    payment_id = int(callback.data.split("_")[1])
    payment = await PaymentManager.get_payment(payment_id)
    if not payment or payment['status'] != 'pending':
        await callback.answer("Payment not found or already processed")
        return
    await PaymentManager.reject_payment(payment_id, callback.from_user.id)
    await callback.bot.send_message(payment['user_id'], "[FAIL] *Payment rejected.* Please contact support or send again.", parse_mode=ParseMode.MARKDOWN)
    await callback.message.edit_text(f"[FAIL] Payment #{payment_id} rejected.")
    await callback.answer()

@router.callback_query(F.data.startswith("view_screenshot_"))
async def view_screenshot(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Unauthorized")
        return
    payment_id = int(callback.data.split("_")[2])
    payment = await PaymentManager.get_payment(payment_id)
    if not payment or not payment['screenshot_file_id']:
        await callback.answer("Screenshot not found")
        return
    await callback.bot.send_photo(callback.from_user.id, payment['screenshot_file_id'], caption=f"Screenshot for payment #{payment_id}")
    await callback.answer()