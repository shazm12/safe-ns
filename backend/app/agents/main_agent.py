from typing import Dict
from PIL import Image
import asyncio
from . import OCRAgent, NSFWAgent, ToxicityAgent
from app.helpers import ImagePreprocessor, PromptInjectionDetector
from typing import Dict, Any
from groq import Groq
import os
import logging


class MainAgent:

    def __init__(self):
        self.ocr_agent = OCRAgent()
        self.nsfw_agent = NSFWAgent()
        self.toxicity_agent = ToxicityAgent()
        self.imagePreprocessor = ImagePreprocessor()
        self.promptInjectionDetector = PromptInjectionDetector()

    async def analyze_image(self, image: Image.Image) -> Dict:

        try:

            processed_image = await self.imagePreprocessor.preprocess(image)

            # process these modules paralelly
            ocr_text, nsfw_result = await asyncio.gather(
                self._run_ocr(processed_image),
                self._run_nsfw(processed_image)
            )

            is_prompt_injection = self.promptInjectionDetector.is_injection(
                ocr_text)

            if (is_prompt_injection):
                raise ValueError("Possible Prompt Injection")

            # Process text toxicity if text exists
            text_result = {}
            if ocr_text and "OCR Error" not in ocr_text:
                text_result = self.toxicity_agent.analyze(ocr_text)
                # Extract offensive words details
                offensive_words = []
                if isinstance(text_result.get("offensive_words"), list):
                    for word_info in text_result["offensive_words"]:
                        if isinstance(word_info, dict):
                            offensive_words.append(word_info.get("word", ""))
                        elif isinstance(word_info, str):
                            offensive_words.append({
                                'word': word_info,
                                'category': 'unknown',
                                'severity': 'low'
                            })

            overall_safeness = nsfw_result.get(
                "is_toxic", False) or text_result.get("is_toxic", False)

            overall_confidence = max(nsfw_result.get(
                "confidence", 0), text_result.get("confidence", 0))

            analysis_json = {
                "image_analysis": nsfw_result,
                "text_analysis": {
                    "extracted_text": ocr_text,
                    "is_toxic": bool(text_result.get("is_toxic", False)),
                    "confidence": float(text_result.get("confidence", 0)),
                    "reasoning": str(text_result.get("reasoning", "No reasoning provided")),
                    "categories": list(text_result.get("categories", [])),
                    "offensive_words": offensive_words,
                    "severity": str(text_result.get("severity", "low")).lower()
                },
                "verdict": overall_safeness
            }

            summary = await self._prepare_summary_data(analysis_json)
            return {"is_toxic": overall_safeness, "confidence": float(overall_confidence), "summary": summary}

        except Exception as e:
            logging.error(e, exc_info=True)
            return {"error": str(e)}

    async def analyze_text(self, text: str) -> str:
        try:
            is_prompt_injection = self.promptInjectionDetector.is_injection(
                text)
            if (is_prompt_injection):
                raise ValueError("Possible Prompt Injection")

            text_result = self.toxicity_agent.analyze(text)
            # Extract offensive words details
            offensive_words = []
            if isinstance(text_result.get("offensive_words"), list):
                for word_info in text_result["offensive_words"]:
                    if isinstance(word_info, dict):
                        offensive_words.append(word_info.get("word", ""))
                    elif isinstance(word_info, str):
                        offensive_words.append({
                            'word': word_info,
                            'category': 'unknown',
                            'severity': 'low'
                        })

            analysis_json = {
                "image_analysis": {},
                "text_analysis": {
                    "extracted_text": text,
                    "is_toxic": bool(text_result.get("is_toxic", False)),
                    "confidence": float(text_result.get("confidence", 0)),
                    "reasoning": str(text_result.get("reasoning", "No reasoning provided")),
                    "categories": list(text_result.get("categories", [])),
                    "offensive_words": offensive_words,
                    "severity": str(text_result.get("severity", "low")).lower()
                },
                "verdict": "unsafe" if bool(text_result.get("is_toxic", False)) else "safe"
            }

            summary = await self._prepare_summary_data(analysis_json)

            return {"is_toxic": bool(text_result.get("is_toxic", False)), "confidence": float(text_result.get("confidence", 0)), "summary": summary}

        except Exception as e:
            logging.error(e, exc_info=True)
            return {"error": f"Text Analysis Error: {str(e)}"}

    async def _prepare_summary_data(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generates an accurate safety summary based on both text and image toxicity analysis results.
        """
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Extract analysis data with proper defaults
        text_analysis = analysis_data.get("text_analysis", {})
        image_analysis = analysis_data.get("image_analysis", {})

        # Text analysis data
        text_toxic = text_analysis.get("is_toxic", False)
        text_confidence = text_analysis.get("confidence", 0)
        text_categories = text_analysis.get("categories", [])
        text_offensive_words = text_analysis.get("offensive_words", [])
        text_reasoning = text_analysis.get(
            "reasoning", "No detailed reasoning provided")
        text_severity = text_analysis.get("severity", "low")

        # Image analysis data
        image_toxic = image_analysis.get("is_toxic", False)
        image_confidence = image_analysis.get("confidence", 0)
        image_flagged_categories = image_analysis.get("flagged_categories", [])
        image_all_categories = image_analysis.get(
            "details", {}).keys() if image_analysis.get("details") else []
        image_reasoning = image_analysis.get(
            "reasoning", "No detailed reasoning provided")
        image_severity = image_analysis.get("severity", "low")
        image_visual_cues = image_analysis.get("visual_cues", [])

        # Build the combined data description with properly mapped categories
        data_lines = [
            "CONTENT SAFETY ANALYSIS SUMMARY:",
            "\nTEXT ANALYSIS:",
            f"- Toxicity Status: {'TOXIC' if text_toxic else 'Non-toxic'}",
            f"- Confidence: {text_confidence:.0%}",
            f"- Categories: {', '.join(text_categories) or 'None'}",
            f"- Offensive Words Count: {len(text_offensive_words)}",
            f"- Severity: {text_severity.upper()}",
            f"- Reasoning: {text_reasoning}",

            "\nIMAGE ANALYSIS:",
            f"- Toxicity Status: {'TOXIC' if image_toxic else 'Non-toxic'}",
            f"- Confidence: {image_confidence:.0%}",
            f"- Flagged Categories: {', '.join(image_flagged_categories) or 'None'}",
            f"- All Categories Checked: {', '.join(image_all_categories) or 'None'}",
            f"- Visual Cues: {', '.join([str(cue) for cue in image_visual_cues]) or 'None'}",
            f"- Severity: {image_severity.upper()}",
            f"- Reasoning: {image_reasoning}"
        ]

        data_description = '\n'.join(data_lines)

        # Determine overall toxicity
        overall_toxic = text_toxic or image_toxic
        overall_confidence = max(text_confidence, image_confidence)

        # Create instructions based on combined analysis
        toxicity_instruction = ("Highlight all concerning elements from both text and image analysis and recommend appropriate restrictions."
                                if overall_toxic else
                                "Note the content appears safe for most audiences based on both text and image analysis.")

        prompt = f"""[INST] <<SYS>>
            You are a content safety analyst. Generate a concise 5-6 sentence summary that:
            1. Clearly states overall safety status considering both text and images
            2. Identifies specific risks from either text or images if toxic
            3. Provides appropriate recommendations based on combined analysis

            Key data:
            {data_description}

            Instructions:
            - Be factual and precise about both text and image findings
            - Never contradict the toxicity analysis
            - Mention if only one component (text or image) is problematic, please talk about only one component or category of text or image in specific that has high likelihood
            - If you do not get likelihood for certain categories of text or image, pick first two from the category list and elaborate more on it.
            - For images, consider both flagged categories and visual cues
            - {toxicity_instruction}
            <</SYS>>

            Generate the combined safety summary[/INST]"""

        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.0,  # Use 0 for maximum consistency
                max_tokens=250  # Slightly more tokens for combined analysis
            )

            summary = response.choices[0].message.content

            # Ensure the summary reflects the toxicity appropriately
            if overall_toxic:
                if "non-toxic" in summary.lower():
                    summary = f"TOXIC CONTENT WARNING: {summary}"
                elif not any(word in summary.lower() for word in ["toxic", "violent", "concern", "risk", "inappropriate"]):
                    summary = f"TOXICITY DETECTED: {summary}"

                # Add clarification if only one component is toxic
                if text_toxic != image_toxic:
                    problematic_component = "text" if text_toxic else "image"
                    summary = f"{problematic_component.upper()}-SPECIFIC ISSUE: {summary}"

            return summary.strip()

        except Exception as e:
            logging.error(e, exc_info=True)
            return {"error": f"Safety evaluation error: {str(e)}"}

    async def _run_ocr(self, image: Image.Image) -> str:
        try:
            return self.ocr_agent.extract_text(image)
        except Exception as e:
            logging.error(e, exc_info=True)
            return {"error": f"OCR Error: {str(e)}"}

    async def _run_nsfw(self, image: Image.Image) -> Dict:
        try:
            return self.nsfw_agent.detect(image)
        except Exception as e:
            logging.error(e, exc_info=True)
            return {"rating": "error", "error": str(e)}
