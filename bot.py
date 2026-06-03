import sys
import io
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.db import db
from handlers import start, free, premium, payment, admin
from utils.expiry import check_and_expire_premium

# Force UTF-8 for Windows console (fixes emoji errors)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.system('chcp 65001 > nul')

logging.basicConfig(level=logging.INFO)

async def expiry_loop():
    while True:
        await asyncio.sleep(3600)
        expired = await check_and_expire_premium()
        if expired:
            logging.info(f"Expired {expired} premium users")

async def main():
    await db.connect()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start.router)
    dp.include_router(free.router)
    dp.include_router(premium.router)
    dp.include_router(payment.router)
    dp.include_router(admin.router)
    asyncio.create_task(expiry_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())