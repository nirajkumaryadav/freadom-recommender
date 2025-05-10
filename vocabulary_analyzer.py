# Note: FastText is optional as it requires a large model download
# This provides a simplified version that works without it

import re
import numpy as np
from collections import Counter

# Word frequency lists by age group (simplified)
SIMPLE_WORDS = set(['the', 'and', 'to', 'a', 'in', 'that', 'is', 'was', 'for', 'on', 
                   'with', 'he', 'she', 'at', 'by', 'from', 'they', 'be', 'or', 'an',
                   'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so',
                   'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when',
                   'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
                   'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
                   'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its',
                   'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our',
                   'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because',
                   'any', 'these', 'give', 'day', 'most', 'us', 'are', 'not', 'has',
                   'had', 'do', 'say', 'have', 'we', 'this', 'it', 'as', 'but', 'of'])

def tokenize_text(text):
    """Simple tokenization function"""
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return words

def assess_vocabulary_difficulty(text, age_range=None):
    """
    Assess vocabulary difficulty using word frequency
    Returns a value between 0 (simple) and 1 (complex)
    """
    words = tokenize_text(text)
    if not words:
        return 0.5  # Default medium difficulty
    
    # Count words that are not in the simple words list
    complex_word_count = sum(1 for word in words if word not in SIMPLE_WORDS)
    
    # Calculate percentage of complex words
    complexity = complex_word_count / len(words)
    
    # Apply age-appropriate scaling
    if age_range:
        if age_range == "5-7":
            # For young readers, even small complexity feels more difficult
            complexity = min(1.0, complexity * 2.0)
        elif age_range == "6-8":
            complexity = min(1.0, complexity * 1.7)
        elif age_range == "7-9":
            complexity = min(1.0, complexity * 1.4)
        elif age_range == "8-10":
            complexity = min(1.0, complexity * 1.2)
        # For older readers, the raw score is appropriate
    
    return complexity

def get_vocabulary_stats(text):
    """Get detailed vocabulary statistics"""
    words = tokenize_text(text)
    if not words:
        return {
            'total_words': 0,
            'unique_words': 0,
            'avg_word_length': 0,
            'complex_word_ratio': 0
        }
    
    word_lengths = [len(word) for word in words]
    unique_words = set(words)
    complex_words = [word for word in words if word not in SIMPLE_WORDS]
    
    return {
        'total_words': len(words),
        'unique_words': len(unique_words),
        'avg_word_length': sum(word_lengths) / len(words),
        'complex_word_ratio': len(complex_words) / len(words)
    }

if __name__ == "__main__":
    # Test function
    sample_text = "The cat sat on the mat. It was happy and purring loudly."
    print(f"Difficulty score: {assess_vocabulary_difficulty(sample_text)}")
    print(f"Vocabulary stats: {get_vocabulary_stats(sample_text)}")