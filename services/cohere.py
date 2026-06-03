import aiohttp
from config import COHERE_API_KEY

class CohereAI:
    def init(self):
        self.api_key = COHERE_API_KEY

    async def generate(self, topic, language, word_limit):
        if not self.api_key:
            raise Exception("Cohere API key missing")
        prompt = f"Write a student assignment on {topic} in {language} with about {word_limit} words."
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "command",
            "prompt": prompt,
            "max_tokens": min(word_limit * 2, 2000),
            "temperature": 0.7
        }
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.cohere.ai/v1/generate", json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"Cohere error {resp.status}: {text[:200]}")
                data = await resp.json()
                return data["generations"][0]["text"].strip()