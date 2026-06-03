from database.db import db
from database.users import UserManager
from datetime import datetime

async def check_and_expire_premium():
    now = datetime.now().isoformat()
    expired_users = await db.fetch_all(
        "SELECT user_id FROM users WHERE is_premium = 1 AND premium_expiry < ?",
        (now,)
    )
    for user in expired_users:
        await UserManager.remove_premium(user['user_id'])
    return len(expired_users)