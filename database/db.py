import aiosqlite
import os
from typing import Optional, Dict, List
from config import DATABASE_PATH

class Database:
    def init(self):   # ✅ double underscores
        self.connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        # Create directory if it doesn't exist (for Railway volume)
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.connection = await aiosqlite.connect(DATABASE_PATH)
        await self._create_tables()

    async def _create_tables(self):
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                country TEXT,
                is_premium BOOLEAN DEFAULT 0,
                premium_plan TEXT,
                premium_expiry TIMESTAMP,
                free_assignments_used INTEGER DEFAULT 0,
                daily_assignments_count INTEGER DEFAULT 0,
                daily_reset_date TIMESTAMP,
                word_limit INTEGER DEFAULT 1000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan_type TEXT,
                amount TEXT,
                currency TEXT,
                screenshot_file_id TEXT,
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                admin_action_by INTEGER
            )
        """)
        await self.connection.commit()

    async def execute(self, query: str, params: tuple = ()):
        async with self.connection.execute(query, params) as cursor:
            await self.connection.commit()
            return cursor

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        async with self.connection.execute(query, params) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        async with self.connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def close(self):
        if self.connection:
            await self.connection.close()

db = Database()