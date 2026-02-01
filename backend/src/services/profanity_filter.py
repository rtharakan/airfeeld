"""
Profanity Filter Service

Basic profanity detection for username validation.
Uses a word list approach with common pattern matching.

Design Notes:
- Extensible word list
- Case-insensitive matching
- Leetspeak detection (basic)
- No external API dependencies for privacy
"""

import re
from functools import lru_cache


# Word list: common English profanity and slurs
# This is intentionally a minimal list - extend as needed
# NOTE: Not listing actual words here for cleanliness
# In production, load from a file that is not committed to repo
PROFANITY_WORDS: set[str] = {
    # Placeholder - load actual words from configuration
    # This prevents offensive words from appearing in source code
}

# Common character substitutions for leetspeak
LEETSPEAK_MAP: dict[str, str] = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "8": "b",
    "@": "a",
    "$": "s",
    "!": "i",
}


def _normalize_text(text: str) -> str:
    """
    Normalize text for profanity matching.
    
    Handles:
    - Lowercase conversion
    - Leetspeak substitution
    - Repeated character removal
    """
    # Lowercase
    normalized = text.lower()
    
    # Replace leetspeak characters
    for leet, normal in LEETSPEAK_MAP.items():
        normalized = normalized.replace(leet, normal)
    
    # Remove repeated characters (e.g., "helllo" -> "helo")
    # Keep at most 2 consecutive same characters
    normalized = re.sub(r"(.)\1{2,}", r"\1\1", normalized)
    
    return normalized


def _extract_words(text: str) -> list[str]:
    """
    Extract potential words from text.
    
    Handles usernames like "badword123" or "my_badword".
    """
    # Split on non-alphanumeric characters
    words = re.split(r"[^a-zA-Z0-9]+", text)
    
    # Also check the whole string without separators
    words.append(re.sub(r"[^a-zA-Z]", "", text))
    
    # Also check for words embedded in numbers
    # e.g., "bad123word" -> "bad", "word"
    alpha_parts = re.findall(r"[a-zA-Z]+", text)
    words.extend(alpha_parts)
    
    return [w for w in words if w]


@lru_cache(maxsize=1024)
def contains_profanity(text: str) -> bool:
    """
    Check if text contains profanity.
    
    Uses cached results for performance on repeated checks.
    
    Args:
        text: Text to check (e.g., username)
    
    Returns:
        True if profanity detected, False otherwise
    """
    if not text:
        return False
    
    # Normalize the input
    normalized = _normalize_text(text)
    
    # Check against word list
    for word in PROFANITY_WORDS:
        if word in normalized:
            return True
    
    # Extract and check individual words
    words = _extract_words(normalized)
    for word in words:
        normalized_word = _normalize_text(word)
        if normalized_word in PROFANITY_WORDS:
            return True
    
    return False


def load_profanity_list(file_path: str) -> None:
    """
    Load profanity words from a file.
    
    File format: one word per line.
    
    Args:
        file_path: Path to profanity word list file
    """
    global PROFANITY_WORDS
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            words = {line.strip().lower() for line in f if line.strip()}
            PROFANITY_WORDS = words
    except FileNotFoundError:
        # Use empty list if file not found
        # Log warning in production
        pass


def add_profanity_word(word: str) -> None:
    """
    Add a word to the profanity list.
    
    Args:
        word: Word to add (will be lowercased)
    """
    PROFANITY_WORDS.add(word.lower())
    # Clear cache when list changes
    contains_profanity.cache_clear()


def remove_profanity_word(word: str) -> None:
    """
    Remove a word from the profanity list.
    
    Args:
        word: Word to remove
    """
    PROFANITY_WORDS.discard(word.lower())
    # Clear cache when list changes
    contains_profanity.cache_clear()


def get_profanity_word_count() -> int:
    """Get the number of words in the profanity list."""
    return len(PROFANITY_WORDS)
