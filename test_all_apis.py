import asyncio
from services.groq import GroqAI
from services.cerebras import CerebrasAI
from services.cohere import CohereAI
from services.deepseek import DeepSeekAI
from services.openrouter import OpenRouterAI
from services.gemini import GeminiAI

async def test_api(name, cls):
    print(f"\n🔍 Testing {name}...")
    try:
        ai = cls()
        result = await ai.generate("test topic", "en", 100)
        print(f"✅ {name} SUCCESS: {result[:100]}...")
        return True
    except Exception as e:
        print(f"❌ {name} FAILED: {e}")
        return False

async def main():
    apis = [
        ("Groq", GroqAI),
        ("Cerebras", CerebrasAI),
        ("Cohere", CohereAI),
        ("DeepSeek", DeepSeekAI),
        ("OpenRouter", OpenRouterAI),
        ("Gemini", GeminiAI),
    ]
    for name, cls in apis:
        await test_api(name, cls)

asyncio.run(main())