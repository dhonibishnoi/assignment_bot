import aiohttp
from config import GROQ_API_KEY

class GroqAI:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        print(f"GroqAI initialized, API key exists: {bool(self.api_key)}")

    async def generate(self, topic, language, word_limit):
        if not self.api_key:
            raise Exception("Groq API key missing")
        
        prompt = f"""You are a professional human assignment writer.
Write like a real student. Avoid AI tone. Make it natural, simple, and academic.
Do not repeat sentences. Make it look handwritten.
Language: {language}
Topic: {topic}
Word limit: approximately {word_limit} words.
Structure: Introduction, Body, Conclusion."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": min(word_limit * 2, 4000)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"Groq error {resp.status}: {text[:200]}")
                data = await resp.json()
                return data["choices"][0]["message"]["content"]