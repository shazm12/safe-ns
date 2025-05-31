from typing import Dict
from PIL import Image
import asyncio
from . import OCRAgent, NSFWAgent, ToxicityAgent
from app.helpers import ImagePreprocessor
from typing import Dict, Any
from groq import Groq
import os


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
        Generates an accurate safety summary based on toxicity analysis results.
        """
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Extract text analysis data with proper defaults
        text_analysis = analysis_data.get("text_analysis", {})
        is_toxic = text_analysis.get("is_toxic", False)
        confidence = text_analysis.get("confidence", 0)
        categories = text_analysis.get("categories", [])
        offensive_words = text_analysis.get("offensive_words", [])
        reasoning = text_analysis.get(
            "reasoning", "No detailed reasoning provided")

        # Build the data description without backslashes
        data_lines = [
            "TEXT ANALYSIS RESULTS:",
            f"- Toxicity Status: {'TOXIC' if is_toxic else 'Non-toxic'}",
            f"- Confidence: {confidence:.0%}",
            f"- Categories: {', '.join(categories) or 'None'}",
            f"- Offensive Words Count: {len(offensive_words)}",
            f"- Primary Reasoning: {reasoning}"
        ]
        
        print(analysis_data)
        data_description = '\n'.join(data_lines)

        # Create instructions
        toxicity_instruction = ("Highlight the concerning elements and recommend restriction."
                                if is_toxic else
                                "Note the content appears safe for most audiences.")

        prompt = (
            "<|im_start|>system\n"
            "You are a content safety analyst. Generate a 3-sentence summary that:\n"
            "1. Clearly states toxicity status\n"
            "2. Identifies specific risks if toxic\n"
            "3. Provides appropriate recommendations\n\n"
            f"Key data:\n{data_description}\n\n"
            "Instructions:\n"
            "- Be factual and precise\n"
            "- Never contradict the toxicity analysis\n"
            f"- {toxicity_instruction}\n"
            "<|im_start|>user\n"
            "Generate the safety summary<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.0,  # Use 0 for maximum consistency
                max_tokens=200
            )

            summary = response.choices[0].message.content

            # Ensure the summary reflects the toxicity
            if is_toxic:
                if "non-toxic" in summary.lower():
                    summary = f"TOXIC CONTENT WARNING: {summary}"
                elif not any(word in summary.lower() for word in ["toxic", "violat", "concern", "risk"]):
                    summary = f"TOXICITY DETECTED: {summary}"

            return summary.strip()

        except Exception as e:
            return f"Safety evaluation error: {str(e)}"

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
