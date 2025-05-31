from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
import json
from dotenv import load_dotenv
from typing import Dict, List
import os



load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")



class ToxicityAgent:
    def __init__(self):
        # Initialize both rule-based and LLM detectors
        self.bad_words = ["fuck", "shit", "hate", "kill"]  # Basic word list
        self.llm = self._init_llm()
        self.prompt = self._init_prompt()

    def _init_llm(self):

        # OpenAI LLM model
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=api_key,
            temperature=0
        )

    def _init_prompt(self):
        return PromptTemplate(
            input_variables=["text"],
            template="""
            Analyze this text for toxicity. Consider:
            1. Explicit profanity
            2. Hate speech
            3. Threats
            4. Sexual content
            5. Harassment
            
            Return JSON format:
            {{
                "is_toxic": bool,
                "categories": list[str],
                "confidence": 0-1,
                "explanation": str
            }}
            
            Text: {text}
            """
        )

    def analyze(self, text: str) -> Dict:
        """Hybrid analysis using rules + LLM"""
        # Rule-based fast check
        found_words = [w for w in self.bad_words if w in text.lower()]
        if found_words:
            return {
                "is_toxic": True,
                "offensive_words": found_words,
                "confidence": 0.95,
                "method": "rule-based"
            }
        
        # LLM deep analysis
        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        try:
            result = chain.run(text=text)
            return self._parse_llm_response(result)
        except Exception as e:
            return {
                "is_toxic": False,
                "error": str(e),
                "method": "fallback"
            }

    def _parse_llm_response(self, response: str) -> Dict:
        try:
            data = json.loads(response.strip())
            return {
                "is_toxic": data.get("is_toxic", False),
                "categories": data.get("categories", []),
                "confidence": data.get("confidence", 0.8),
                "method": "llm"
            }
        except:
            return {
                "is_toxic": "error" in response.lower(),
                "error": "Invalid LLM response",
                "raw_response": response
            }