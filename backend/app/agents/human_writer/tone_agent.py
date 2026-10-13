"""
AI IMP NEWS OS
Tone Agent
Version: 2.0

Text ko thoda cleaner / more human banata hai (light pass).
"""

import re


def improve_tone(text):
    """
    Light tone cleanup:
    - extra spaces hatao
    - repeated punctuation fix
    - very robotic phrases soften
    """
    if not text:
        return ""

    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.replace("!!", "!")
    cleaned = cleaned.replace("??", "?")

    replacements = {
        "In conclusion,": "Bottom line:",
        "It is important to note that": "Note that",
        "Furthermore,": "Also,",
        "Additionally,": "Plus,",
        "Leverage": "Use",
        "utilize": "use",
        "revolutionary": "notable",
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    return cleaned.strip()


if __name__ == "__main__":
    sample = "Furthermore,   it is important to note that AI will utilize new tools!!"
    print(improve_tone(sample))