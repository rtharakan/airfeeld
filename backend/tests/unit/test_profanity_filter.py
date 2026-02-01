"""
Unit Tests for Profanity Filter

Tests profanity detection with various obfuscation techniques.
"""

import pytest

from src.services.profanity_filter import (
    add_profanity_word,
    contains_profanity,
    get_profanity_word_count,
    remove_profanity_word,
)


class TestContainsProfanity:
    """Tests for profanity detection."""
    
    def test_empty_string_is_clean(self) -> None:
        """Empty string should not contain profanity."""
        assert contains_profanity("") is False
    
    def test_clean_username_passes(self) -> None:
        """Normal usernames should pass."""
        assert contains_profanity("pilot123") is False
        assert contains_profanity("aviator_fan") is False
        assert contains_profanity("SkyWatcher42") is False
    
    def test_detects_direct_match(self) -> None:
        """Should detect words directly in the list."""
        # Add a test word
        add_profanity_word("badword")
        
        assert contains_profanity("badword") is True
        
        # Cleanup
        remove_profanity_word("badword")
    
    def test_case_insensitive(self) -> None:
        """Detection should be case-insensitive."""
        add_profanity_word("badword")
        
        assert contains_profanity("BADWORD") is True
        assert contains_profanity("BadWord") is True
        assert contains_profanity("bAdWoRd") is True
        
        remove_profanity_word("badword")
    
    def test_detects_embedded_words(self) -> None:
        """Should detect profanity embedded in usernames."""
        add_profanity_word("bad")
        
        assert contains_profanity("mybadname") is True
        assert contains_profanity("bad123") is True
        assert contains_profanity("123bad") is True
        
        remove_profanity_word("bad")
    
    def test_detects_leetspeak(self) -> None:
        """Should detect basic leetspeak substitutions."""
        add_profanity_word("test")
        
        # Common substitutions
        assert contains_profanity("t3st") is True  # e -> 3
        assert contains_profanity("te5t") is True  # s -> 5
        assert contains_profanity("t3s7") is True  # e->3, t->7
        
        remove_profanity_word("test")
    
    def test_detects_repeated_characters(self) -> None:
        """Should detect words with repeated characters."""
        add_profanity_word("test")
        
        assert contains_profanity("teeest") is True
        assert contains_profanity("tessst") is True
        
        remove_profanity_word("test")
    
    def test_handles_special_characters(self) -> None:
        """Should handle usernames with special characters."""
        add_profanity_word("bad")
        
        assert contains_profanity("my_bad_name") is True
        assert contains_profanity("bad-word") is True
        
        remove_profanity_word("bad")


class TestWordListManagement:
    """Tests for word list management functions."""
    
    def test_add_word(self) -> None:
        """Should add word to the list."""
        initial_count = get_profanity_word_count()
        add_profanity_word("uniqueword123")
        
        assert get_profanity_word_count() == initial_count + 1
        assert contains_profanity("uniqueword123") is True
        
        # Cleanup
        remove_profanity_word("uniqueword123")
    
    def test_remove_word(self) -> None:
        """Should remove word from the list."""
        add_profanity_word("removetest")
        assert contains_profanity("removetest") is True
        
        remove_profanity_word("removetest")
        assert contains_profanity("removetest") is False
    
    def test_add_lowercases_word(self) -> None:
        """Added words should be lowercased."""
        add_profanity_word("UPPERCASE")
        
        # Should match lowercase
        assert contains_profanity("uppercase") is True
        
        remove_profanity_word("uppercase")
    
    def test_remove_handles_missing_word(self) -> None:
        """Removing non-existent word should not error."""
        # Should not raise
        remove_profanity_word("nonexistentword12345")


class TestCaching:
    """Tests for cache behavior."""
    
    def test_cache_returns_consistent_results(self) -> None:
        """Same input should return cached result."""
        # Call multiple times - should use cache
        result1 = contains_profanity("test_username")
        result2 = contains_profanity("test_username")
        
        assert result1 == result2
    
    def test_cache_cleared_on_add(self) -> None:
        """Cache should be cleared when word list changes."""
        # Establish cached result
        assert contains_profanity("newword123") is False
        
        # Add word (should clear cache)
        add_profanity_word("newword123")
        
        # New result should reflect change
        assert contains_profanity("newword123") is True
        
        # Cleanup
        remove_profanity_word("newword123")
