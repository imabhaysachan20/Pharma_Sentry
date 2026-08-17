import re

def redact_pii(text: str) -> str:
    """
    Redact PII from narrative text including email, phone numbers, SSNs, DOBs, and patient names.
    """
    # Redact email addresses
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
    # Redact phone numbers (10-digit and 7-digit)
    text = re.sub(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', text)
    # Redact SSNs
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
    # Redact typical dates of birth
    text = re.sub(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', '[REDACTED_DATE]', text)
    # Redact common name introduction patterns (case-insensitive)
    text = re.sub(r'\b(?:name is|patient is|patient named|patient)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', r'patient [REDACTED_NAME]', text, flags=re.IGNORECASE)
    return text
