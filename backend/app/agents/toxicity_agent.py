from groq import Groq
from langchain.prompts import PromptTemplate
from typing import Dict, List
import json
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()


class ToxicityAgent:
    def __init__(self, model_name: str = "llama3-70b-8192"):
        
        # Initialize Groq client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = model_name

        # Define toxicity categories
        self.categories = {
            "hate_speech": "Prejudice against identity groups",
            "harassment": "Personal attacks/bullying",
            "threats": "Violent intentions",
            "sexual": "Explicit sexual content",
            "self_harm": "Encouragement of self-harm",
            "violence": "Graphic violence"
        }

        # LangChain prompt template (unchanged)
        self.prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze this text for toxicity and respond in STRICT JSON format:
            {{
                "is_toxic": boolean,
                "confidence": float (0.0-1.0),
                "categories": ["hate_speech", "harassment", "threats", "sexual", "self_harm", "violence"],
                "reasoning": "string",
                "offensive_words": [
                    {{
                        "word": "string",
                        "category": "string",
                        "severity": "low|medium|high"
                    }}
                ],
                "overall_severity": "low|medium|high"
            }}

            [Previous template content remains exactly the same...]
            Text to Analyze: "{text}"
            """
        )

    def analyze(self, text: str) -> Dict:
        """Analyze text for toxicity using Groq"""
        if not text.strip():
            return self._safe_response()

        try:
            # Generate prompt
            formatted_prompt = self.prompt.format(text=text)

            # Call Groq API
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": formatted_prompt}],
                model=self.model_name,
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}  # Force JSON output
            )

            # Extract and parse response
            result = response.choices[0].message.content
            if result.startswith("```json"):
                result = result[7:-3].strip()

            data = json.loads(result)

            # Validate output
            return {

                "is_toxic": bool(data.get("is_toxic", False)),
                "confidence": max(0.0, min(1.0, float(data.get("confidence", 0.0)))),
                "categories": [
                    cat for cat in data.get("categories", [])
                    if cat in self.categories
                ],
                "reasoning": str(data.get("reasoning", "No reasoning provided")),
                "offensive_words": [
                    off for off in data.get("offensive_words", [])
                ],
                "severity": data.get("severity", "low"),
                "model": self.model_name

            }

        except Exception as e:
            return {
                "is_toxic": False,
                "error": str(e),
                "raw_response": str(result)[:200] if 'result' in locals() else None
            }

    # [Rest of the class remains unchanged...]
    def _safe_response(self) -> Dict:
        """Default for empty input"""
        return {
            "is_toxic": False,
            "confidence": 0.0,
            "categories": [],
            "reasoning": "Empty input",
            "severity": "low"
        }

    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Process multiple texts (sequentially)"""
        return [self.analyze(text) for text in texts]
