# services/fallback.py
import random

class FallbackAI:
    async def generate(self, topic: str, language: str, word_limit: int) -> str:
        """
        Fallback generator when all real AI APIs fail.
        Returns a basic assignment text (not repetitive, but templated).
        """
        templates = [
            f"This assignment explores the topic '{topic}' in detail. "
            f"The introduction sets the context and explains why '{topic}' is important. "
            f"The body discusses key aspects, including definitions, historical background, and current applications. "
            f"Finally, the conclusion summarizes the main points and suggests areas for further research. "
            f"The assignment is written in {language} and follows a natural, student‑like style.",

            f"'{topic}' is a significant subject that deserves careful analysis. "
            f"This paper begins by defining core concepts and outlining the scope of the study. "
            f"Subsequent sections present evidence, case studies, and critical evaluation. "
            f"The conclusion ties together the findings and offers recommendations. "
            f"Word limit: approximately {word_limit} words. Language: {language}.",

            f"An in‑depth look at {topic}. "
            f"The first part introduces the main ideas and questions. "
            f"The second part examines real‑world examples and academic perspectives. "
            f"The third part discusses implications and limitations. "
            f"The final part concludes the assignment. "
            f"This text is generated as a fallback because the primary AI services are unavailable. "
            f"Language: {language}. Target length: {word_limit} words."
        ]
        return random.choice(templates)