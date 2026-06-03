from langdetect import detect, DetectorFactory
import re

DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    try:
        if re.search(r'[\u0600-\u06FF\u0900-\u097F\u4e00-\u9fff]', text):
            lang = detect(text)
            return lang if lang in ['hi', 'ar', 'zh-cn', 'es', 'fr'] else 'en'
        return 'en'
    except:
        return 'en'