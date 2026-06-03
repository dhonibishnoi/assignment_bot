import aiohttp
from config import DEEPSEEK_API_KEY

class DeepSeekAI:
    def init(self):
        self.api_key = DEEPSEEK_API_KEY

    async def generate(self, topic, language, word_limit):
        if not self.api_key:
            raise Exception("DeepSeek API key missing")
        prompt = f"Write a student assignment on {topic} in {language} with about {word_limit} words."
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": min(word_limit * 2, 2000)
        }
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.deepseek.com/v1/chat/completions", json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"DeepSeek error {resp.status}: {text[:200]}")
                data = await resp.json()
                return data["choices"][0]["message"]["content"]