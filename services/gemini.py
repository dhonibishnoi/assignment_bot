from google import genai
from config import GEMINI_API_KEY

class GeminiAI:
    def init(self):
        self.api_key = GEMINI_API_KEY

    async def generate(self, topic, language, word_limit):
        if not self.api_key:
            raise Exception("Gemini API key missing")
        prompt = f"Write a student assignment on {topic} in {language} with about {word_limit} words."
        client = genai.Client(api_key=self.api_key)
        response = await client.aio.models.generate_content(model="models/gemini-2.0-flash", contents=prompt)
        return response.text