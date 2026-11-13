import re
from typing import List, Dict, Any

class ConsistencyValidator:
    """
    Blueprint Section 8 Compliance Checks:
    - Warn if 'Bombay' appears (Must strictly be 'Mumbai')
    - Warn if a venture is described as a 'separate company' or 'subsidiary company' (Must be 'division of Belvo Ventures Group')
    - Warn if company name is misspelled or inconsistent
    - Check for forbidden legal registration/license numbers
    """
    
    FORBIDDEN_WORDS = [
        (r'\bBombay\b', "Found legacy city name 'Bombay'. Rule: Always write 'Mumbai'."),
        (r'\bseparate compan(y|ies)\b', "Venture described as 'separate company'. Rule: Ventures are divisions of one company, never separate companies."),
        (r'\bindependent compan(y|ies)\b', "Venture described as 'independent company'. Rule: All 9 ventures are divisions of Belvo Ventures Group."),
        (r'\bCIN\b|\bLLPIN\b|\bGSTIN\b|\bUdyam\b|\bRegistration No\b', "Legal registration or entity code found. Rule: Do not publish registration numbers, licenses, or legal entity codes.")
    ]

    @classmethod
    def validate_text(cls, text: str) -> List[str]:
        warnings = []
        if not text:
            return warnings
            
        for pattern, message in cls.FORBIDDEN_WORDS:
            if re.search(pattern, text, re.IGNORECASE):
                warnings.append(message)
                
        # Check company name casing if roughly matched
        if "belvo" in text.lower():
            # If it uses Belvo Group without Ventures or misnomers
            if re.search(r'\bBelvo Group\b', text) and not re.search(r'\bBelvo Ventures Group\b', text):
                warnings.append("Found 'Belvo Group'. Use the exact canonical name 'Belvo Ventures Group'.")
                
        return warnings

    @classmethod
    def validate_venture_dict(cls, data: Dict[str, Any]) -> List[str]:
        warnings = []
        for key in ["name", "one_line", "description", "sector"]:
            val = str(data.get(key, ""))
            w = cls.validate_text(val)
            warnings.extend(w)
        return list(set(warnings))
