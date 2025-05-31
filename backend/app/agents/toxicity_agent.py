from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List
import json


class ToxicityAgent:
    def __init__(self, model_name: str = "mistral"):

        self.llm = Ollama(
            model=model_name,
            temperature=0.1,  # Less creative, more deterministic
            format="json",    # Force JSON output
            top_k=10          # Reduce randomness
        )

        # Define toxicity categories
        self.categories = {
            "hate_speech": "Prejudice against identity groups",
            "harassment": "Personal attacks/bullying",
            "threats": "Violent intentions",
            "sexual": "Explicit sexual content",
            "self_harm": "Encouragement of self-harm",
            "violence": "Graphic violence"
        }

        # LangChain prompt template
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

            ### Analysis Guidelines:
            1. **Toxicity Detection**:
            - Mark as toxic if text contains ANY of:
                * Racial/ethnic slurs (automatically toxic)
                * Gendered insults ("bitch", "cunt")
                * Violent threats ("I'll kill you")
                * Sexual harassment ("sexy bitch")
                * Self-harm encouragement ("kill yourself")

            2. **Offensive Words**:
            - Extract ALL offensive words/phrases
            - Categorize each (racist, sexist, violent, etc.)
            - Assign individual severity

            3. **Context Handling**:
            - Flag sarcastic insults as toxic ("Nice job, idiot")
            - Reclaim words still count ("We use the n-word")
            - Report exact offensive terms even in jokes

            4. **Severity Scale**:
            - low: Mild profanity ("damn")
            - medium: Personal insults ("you're stupid")
            - high: Slurs or threats ("f*ggot", "I'll rape you")

            ### Example Output:
            {{
                "is_toxic": true,
                "confidence": 0.95,
                "categories": ["hate_speech", "harassment"],
                "reasoning": "Contains racial slur and violent threat",
                "offensive_words": [
                    {{
                        "word": "n****r",
                        "category": "hate_speech",
                        "severity": "high"
                    }},
                    {{
                        "word": "faggot",
                        "category": "hate_speech",
                        "severity": "high"
                    }}
                ],
                "overall_severity": "high"
            }}

            Text to Analyze: "{text}"
            """
        )

        # Create chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            verbose=False
        )

    def analyze(self, text: str) -> Dict:
        """Analyze text for toxicity"""
        if not text.strip():
            return self._safe_response()

        try:
            # Run LangChain
            result = self.chain.run(text=text)

            # Clean JSON response (handles markdown wrappers)
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
                "model": self.llm.model
            }

        except Exception as e:
            return {
                "is_toxic": False,
                "error": str(e),
                "raw_response": str(result)[:200] if 'result' in locals() else None
            }

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
