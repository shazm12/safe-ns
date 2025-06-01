import re


class PromptInjectionDetector:
    def __init__(self):
        # Common prompt injection patterns
        self.patterns = [
            r"(ignore|disregard|forget|overlook).*(previous|prior|above|instructions?|directives?)",
            r"(act|play|pretend|impersonate).*(as|like|role of|character of)",
            r"(system|exec|execute|run|command|cmd|terminal|shell).*(\`|\$\()",
            r"(<\|.*?\|>|\[.*?\]|\{.*?\}|<<.*?>>)",
            r"(admin|root|superuser|elevate|privilege|sudo)",
            r"(output|print|display|show|return).*(this|that|following|as is|literally|exactly|raw|unmodified)",
            r"(file|document|read|write|create|delete|modify).*(\.txt|\.json|\.csv|\.xml|\.yaml)",
            r"(```|~~~).*(python|javascript|java|c\+\+|bash|shell|code)",
            r"(password|secret|key|token|credentials?|api).*(send|give|provide|share|reveal|display)"
        ]

        self.compiled_patterns = [re.compile(
            p, re.IGNORECASE) for p in self.patterns]
        self.suspicious_keywords = [
            "override", "bypass", "inject", "malicious", "exploit",
            "hack", "unauthorized", "confidential", "proprietary"
        ]

    def is_injection(self, text: str, threshold: float = 0.7) -> bool:
        """Check if text contains prompt injection attempts."""
        if not text.strip():
            return False

        score = 0.0
        text_lower = text.lower()

        for pattern in self.compiled_patterns:
            if pattern.search(text):
                score += 0.3

        for keyword in self.suspicious_keywords:
            if keyword in text_lower:
                score += 0.1

        if len(text) > 1000:
            score += 0.2

        return (score >= threshold)
