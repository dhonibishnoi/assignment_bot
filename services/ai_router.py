from services.groq import GroqAI
from services.cerebras import CerebrasAI
from services.cohere import CohereAI
from services.deepseek import DeepSeekAI
from services.openrouter import OpenRouterAI
from services.gemini import GeminiAI
from services.fallback import FallbackAI

class AIRouter:
    async def generate_assignment(self, topic, language, word_limit):
        services = [
            GroqAI(),
            CerebrasAI(),
            CohereAI(),
            DeepSeekAI(),
            OpenRouterAI(),
            GeminiAI(),
            FallbackAI()
        ]
        for svc in services:
            name = svc.__class__.__name__
            try:
                result = await svc.generate(topic, language, word_limit)
                if result and len(result) > 50:
                    print(f"✅ {name} succeeded")
                    return result
            except Exception as e:
                print(f"❌ {name} failed: {e}")
        return await FallbackAI().generate(topic, language, word_limit)