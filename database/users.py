from database.db import db
from datetime import datetime, timedelta
from config import FREE_LIMIT, PREMIUM_DAILY_LIMIT

class UserManager:
    @staticmethod
    async def get_user(user_id: int):
        return await db.fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))

    @staticmethod
    async def create_user(user_id: int, username: str, first_name: str, country: str):
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, country, word_limit) VALUES (?, ?, ?, ?, 1000)",
            (user_id, username, first_name, country)
        )
        return await UserManager.get_user(user_id)

    @staticmethod
    async def update_country(user_id: int, country: str):
        await db.execute("UPDATE users SET country = ? WHERE user_id = ?", (country, user_id))

    @staticmethod
    async def increment_free_usage(user_id: int):
        await db.execute(
            "UPDATE users SET free_assignments_used = free_assignments_used + 1 WHERE user_id = ?",
            (user_id,)
        )

    @staticmethod
    async def increment_daily_count(user_id: int):
        today = datetime.now().date().isoformat()
        user = await UserManager.get_user(user_id)
        if user and user.get("daily_reset_date") != today:
            await db.execute(
                "UPDATE users SET daily_assignments_count = 1, daily_reset_date = ? WHERE user_id = ?",
                (today, user_id)
            )
        else:
            await db.execute(
                "UPDATE users SET daily_assignments_count = daily_assignments_count + 1 WHERE user_id = ?",
                (user_id,)
            )

    @staticmethod
    async def check_free_limit(user_id: int) -> bool:
        user = await UserManager.get_user(user_id)
        if not user:
            return False
        return user.get("free_assignments_used", 0) < FREE_LIMIT

    @staticmethod
    async def check_premium_daily_limit(user_id: int) -> bool:
        user = await UserManager.get_user(user_id)
        if not user or not user.get("is_premium"):
            return False
        today = datetime.now().date().isoformat()
        reset_date = user.get("daily_reset_date")
        if reset_date != today:
            return True
        return user.get("daily_assignments_count", 0) < PREMIUM_DAILY_LIMIT

    @staticmethod
    async def activate_premium(user_id: int, plan: str, expiry_days: int):
        expiry = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        await db.execute(
            "UPDATE users SET is_premium = 1, premium_plan = ?, premium_expiry = ?, free_assignments_used = 0, daily_assignments_count = 0 WHERE user_id = ?",
            (plan, expiry, user_id)
        )

    @staticmethod
    async def remove_premium(user_id: int):
        await db.execute(
            "UPDATE users SET is_premium = 0, premium_plan = NULL, premium_expiry = NULL WHERE user_id = ?",
            (user_id,)
        )
    
    @staticmethod
    async def update_word_limit(user_id: int, word_limit: int):
        await db.execute("UPDATE users SET word_limit = ? WHERE user_id = ?", (word_limit, user_id))