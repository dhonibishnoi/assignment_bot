import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

# All API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

UPI_ID = os.getenv("UPI_ID", "example@upi")
USD_WALLET = os.getenv("USD_WALLET", "0x...ETH")

FREE_LIMIT = 2
PREMIUM_DAILY_LIMIT = 15
DEFAULT_WORD_LIMIT = 1000

# Database path - Railway persistent volume
if os.path.exists('/railway') or os.getenv('RAILWAY_VOLUME_MOUNT_PATH'):
    DATABASE_PATH = '/app/data/assignment_bot.db'
else:
    DATABASE_PATH = 'assignment_bot.db'

SCREENSHOTS_DIR = "storage/screenshots"

PRICE_1M_INR = 199
PRICE_3M_INR = 499
PRICE_1M_USD = 5
PRICE_3M_USD = 12