import aiohttp
from config import CEREBRAS_API_KEY

class CerebrasAI:
    def init(self):
        self.api_key = CEREBRAS_API_KEY

    async def generate(self, topic, language, word_limit):
        if not self.api_key:
            raise Exception("Cerebras API key missing")
        prompt = f"Write a student assignment on {topic} in {language} with about {word_limit} words."
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama3.1-8b",
            "prompt": prompt,
            "max_tokens": min(word_limit * 2, 2000),
            "temperature": 0.7
        }
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.cerebras.ai/v1/completions", json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"Cerebras error {resp.status}: {text[:200]}")
                data = await resp.json()
                return data["choices"][0]["text"].strip()