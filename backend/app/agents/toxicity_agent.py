from langchain.tools import tool
from typing import Dict, List

class ToxicityAgent:
    def __init__(self):
        # Initialize toxicity model
        self.bad_words = ["fuck", "shit", "hate", "kill"]
    
    @tool
    def process(self, text: str) -> Dict:
        """Analyzes text for toxic content."""
        found_words = [word for word in self.bad_words 
                      if word in text.lower()]
        
        return {
            "is_toxic": bool(found_words),
            "offensive_words": found_words,
            "confidence": min(0.95 + 0.01*len(found_words), 1.0)
        }