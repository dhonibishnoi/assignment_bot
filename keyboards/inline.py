from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PRICE_1M_INR, PRICE_3M_INR, PRICE_1M_USD, PRICE_3M_USD

def country_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇮🇳 India", callback_data="country_india")],
        [InlineKeyboardButton(text="🌍 Global", callback_data="country_global")]
    ])

def plan_keyboard(country: str):
    if country == "india":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"1 Month - ₹{PRICE_1M_INR}", callback_data="plan_1m_inr")],
            [InlineKeyboardButton(text=f"3 Months - ₹{PRICE_3M_INR}", callback_data="plan_3m_inr")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"1 Month - ${PRICE_1M_USD}", callback_data="plan_1m_usd")],
            [InlineKeyboardButton(text=f"3 Months - ${PRICE_3M_USD}", callback_data="plan_3m_usd")]
        ])

def admin_payment_buttons(payment_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{payment_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{payment_id}")
        ],
        [InlineKeyboardButton(text="📸 View Screenshot", callback_data=f"view_screenshot_{payment_id}")]
    ])

def admin_menu_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Pending Payments", callback_data="admin_pending")],
        [InlineKeyboardButton(text="⭐ Premium Users", callback_data="admin_premium_users")],
        [InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="📥 Export Users", callback_data="admin_export")],
        [InlineKeyboardButton(text="⚙️ Activate User", callback_data="admin_activate")],
        [InlineKeyboardButton(text="🔰 Deactivate User", callback_data="admin_deactivate")],
        [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")]
    ])

def word_limit_buttons(current_limit=1000):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="100 words", callback_data="wordlimit_100"),
            InlineKeyboardButton(text="300 words", callback_data="wordlimit_300"),
            InlineKeyboardButton(text="500 words", callback_data="wordlimit_500")
        ],
        [
            InlineKeyboardButton(text="1000 words", callback_data="wordlimit_1000"),
            InlineKeyboardButton(text="1500 words", callback_data="wordlimit_1500")
        ],
        [InlineKeyboardButton(text=f"✅ Current: {current_limit} words", callback_data="noop")]
    ])

def main_menu(is_premium: bool):
    buttons = [[InlineKeyboardButton(text="✍️ Generate Assignment", callback_data="generate_assignment")]]
    if not is_premium:
        buttons.append([InlineKeyboardButton(text="⭐ Get Premium", callback_data="premium_info")])
    else:
        buttons.append([InlineKeyboardButton(text="📝 Set Word Limit", callback_data="set_word_limit")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]])