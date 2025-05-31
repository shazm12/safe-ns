from typing import Dict
from PIL import Image
import asyncio
from . import OCRAgent, NSFWAgent, ToxicityAgent
from app.helpers import ImagePreprocessor
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from typing import Dict, Any
import json


class MainAgent:

    def __init__(self):
        self.ocr_agent = OCRAgent()
        self.nsfw_agent = NSFWAgent()
        self.toxcity_agent = ToxicityAgent()
        self.imagePreprocessor = ImagePreprocessor()

    async def analyze_image(self, image: Image.Image) -> Dict:

        try:

            processed_image = await self.imagePreprocessor.preprocess(image)

            # process these modules paralelly
            ocr_text, nsfw_result = await asyncio.gather(
                self._run_ocr(processed_image),
                self._run_nsfw(processed_image)
            )

            # Process text toxicity if text exists
            text_result = {}
            if ocr_text and "OCR Error" not in ocr_text:
                text_result = self.toxcity_agent.analyze(ocr_text)

            analysis_json = {
                "image_analysis": nsfw_result,
                "text_analysis": {
                    "extracted_text": ocr_text,
                    "is_toxic": text_result.get("is_toxic", False),
                    "reasoning": text_result.get("reasoning", ""),
                    "offensive_words": text_result.get("offensive_words", [])
                },
                "verdict": "unsafe" if (
                    nsfw_result.get("rating") == "unsafe" or
                    text_result.get("is_toxic", False)
                ) else "safe"
            }

            summary = self._prepare_summary_data(analysis_json)

            return summary

        except Exception as e:
            return {"error": str(e)}

    async def analyze_text(self, text):
        try:
            text_result = self.toxcity_agent.analyze(text)
            analysis_json = {
                "image_analysis": None,
                "text_analysis": {
                    "extracted_text": text,
                    "is_toxic": text_result.get("is_toxic", False),
                    "reasoning": text_result.get("reasoning", ""),
                    "offensive_words": text_result.get("offensive_words", [])
                },
                "verdict": "unsafe" if (
                    text_result.get("is_toxic", False)
                ) else "safe"
            }
            return self._prepare_summary_data(analysis_json)
        except Exception as e:
            return {f"Text Analysis Error: {e}"}

    def _prepare_summary_data(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generates a human-readable safety summary from NSFW/text analysis results.

        Args:
            analysis_data: The combined image/text analysis output

        Returns:
            str: Concise summary paragraph highlighting risks without JSON formatting
        """
        llm = Ollama(model="mistral")

        # Convert analysis_data to string and escape curly braces to prevent variable interpretation
        analysis_str = json.dumps(analysis_data, indent=2).replace(
            "{", "{{").replace("}", "}}")

        template = """[INST] Analyze this content safety report and generate a concise 3-4 sentence paragraph summary. 
        Highlight critical risks while being professional. Structure your response as a plain text paragraph only.

        Focus on:
        - Image rating and flagged categories
        - Toxic text or offensive words
        - Overall safety verdict

        Provide ONLY the summary paragraph - no JSON, no formatting, no additional explanations.

        Data:
        {analysis_data}
        [/INST]"""

        prompt = PromptTemplate(
            input_variables=["analysis_data"],
            template=template
        )

        chain = prompt | llm
        result = chain.invoke({"analysis_data": analysis_str})

        return result.strip()

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
