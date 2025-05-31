from typing import Dict
from PIL import Image
import asyncio
from . import OCRAgent, NSFWAgent, ToxicityAgent
from app.helpers import ImagePreprocessor

class MainAgent:
    def __init__(self):        
        self.ocr_agent = OCRAgent()
        self.nsfw_agent = NSFWAgent()
        self.toxcity_agent = ToxicityAgent()

    async def analyze(self, image: Image.Image) -> Dict:

        try:
            
            processed_image = await ImagePreprocessor
            
            # process these modules paralelly
            ocr_text, nsfw_result = await asyncio.gather(
                self._run_ocr(processed_image),
                self._run_nsfw(processed_image)
            )
            
            # Process text toxicity if text exists
            text_result = {}
            if ocr_text and "OCR Error" not in ocr_text:
                text_result = self.toxcity_agent.analyze(ocr_text)
            
            return {
                "image_analysis": nsfw_result,
                "text_analysis": {
                    "extracted_text": ocr_text,
                    "is_toxic": text_result.get("is_toxic", False),
                    "offensive_words": text_result.get("offensive_words", [])
                },
                "verdict": "unsafe" if (
                    nsfw_result.get("rating") == "unsafe" or
                    text_result.get("is_toxic", False)
                ) else "safe"
            }
            
        except Exception as e:
            return {"error": str(e)}

    async def _run_ocr(self, image: Image.Image) -> str:
        try:
            return self.ocr_agent.extract_text(image)
        except Exception as e:
            return f"OCR Error: {str(e)}"

    async def _run_nsfw(self, image: Image.Image) -> Dict:
        try:
            return self.nsfw_agent.detect(image)
        except Exception as e:
            return {"rating": "error", "error": str(e)}