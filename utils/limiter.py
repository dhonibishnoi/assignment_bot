from database.users import UserManager
from config import FREE_LIMIT, PREMIUM_DAILY_LIMIT

class Limiter:
    @staticmethod
    async def can_generate(user_id: int, is_premium: bool) -> tuple[bool, str]:
        if not is_premium:
            if await UserManager.check_free_limit(user_id):
                return True, "free"
            else:
                return False, f"Free limit reached ({FREE_LIMIT} assignments max). Please upgrade to premium."
        else:
            if await UserManager.check_premium_daily_limit(user_id):
                return True, "premium"
            else:
                return False, f"Daily limit reached ({PREMIUM_DAILY_LIMIT} assignments/day). Please try tomorrow."

    @staticmethod
    async def record_generation(user_id: int, is_premium: bool):
        if is_premium:
            await UserManager.increment_daily_count(user_id)
        else:
            await UserManager.increment_free_usage(user_id)