from database.db import db
from typing import List, Dict

class PaymentManager:
    @staticmethod
    async def create_payment(user_id: int, plan_type: str, amount: str, currency: str, screenshot_file_id: str, payment_method: str):
        await db.execute(
            "INSERT INTO payments (user_id, plan_type, amount, currency, screenshot_file_id, payment_method) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, plan_type, amount, currency, screenshot_file_id, payment_method)
        )
        return await db.fetch_one("SELECT last_insert_rowid() as id")

    @staticmethod
    async def get_pending_payments() -> List[Dict]:
        return await db.fetch_all("SELECT * FROM payments WHERE status = 'pending' ORDER BY timestamp ASC")

    @staticmethod
    async def get_payment(payment_id: int):
        return await db.fetch_one("SELECT * FROM payments WHERE id = ?", (payment_id,))

    @staticmethod
    async def approve_payment(payment_id: int, admin_id: int):
        await db.execute(
            "UPDATE payments SET status = 'approved', admin_action_by = ? WHERE id = ?",
            (admin_id, payment_id)
        )

    @staticmethod
    async def reject_payment(payment_id: int, admin_id: int):
        await db.execute(
            "UPDATE payments SET status = 'rejected', admin_action_by = ? WHERE id = ?",
            (admin_id, payment_id)
        )
