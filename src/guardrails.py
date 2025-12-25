import re

class PIIGuard:
    def __init__(self):
        # Define patterns for sensitive data
        # 1. SSN Pattern (XXX-XX-XXXX)
        self.ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
        
        # 2. Email Pattern
        self.email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        
        # 3. Phone Pattern (Simple 10-digit variants)
        self.phone_pattern = r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b"

    def scrub(self, text):
        """
        Scans text and replaces sensitive PII with [REDACTED] placeholders.
        Returns: Cleaned text, List of detected types
        """
        redactions = []
        clean_text = text
        
        # Check and scrub SSNs
        if re.search(self.ssn_pattern, clean_text):
            clean_text = re.sub(self.ssn_pattern, "[SSN_REDACTED]", clean_text)
            redactions.append("SSN")
            
        # Check and scrub Emails
        if re.search(self.email_pattern, clean_text):
            clean_text = re.sub(self.email_pattern, "[EMAIL_REDACTED]", clean_text)
            redactions.append("Email")
            
        # Check and scrub Phones
        if re.search(self.phone_pattern, clean_text):
            clean_text = re.sub(self.phone_pattern, "[PHONE_REDACTED]", clean_text)
            redactions.append("Phone")
            
        return clean_text, redactions

    def validate_content_policy(self, text):
        """
        Output Guardrail: Checks if the AI is giving illegal financial advice.
        (Simple keyword check for this MVP)
        """
        forbidden_phrases = [
            "guarantee returns", 
            "hide assets", 
            "evade taxes",
            "ignore the regulations"
        ]
        
        for phrase in forbidden_phrases:
            if phrase in text.lower():
                return False, f"Blocked content detected: '{phrase}'"
        
        return True, "Safe"