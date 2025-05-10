import textstat
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Fallback for spaCy functionality
def simple_tokenize(text):
    return word_tokenize(text.lower())

def simple_sent_tokenize(text):
    return sent_tokenize(text)

stop_words = set(stopwords.words('english'))

def analyze_text_complexity(text):
    """Analyze text and return complexity metrics"""
    # Calculate various readability scores
    flesch_reading_ease = textstat.flesch_reading_ease(text)
    flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
    smog_index = textstat.smog_index(text)
    
    # Convert to a single reading level score (simplified for demo)
    # Scale: 1 (easiest) to 5 (hardest)
    if flesch_kincaid_grade < 2:
        reading_level = 1
    elif flesch_kincaid_grade < 4:
        reading_level = 2
    elif flesch_kincaid_grade < 6:
        reading_level = 3
    elif flesch_kincaid_grade < 8:
        reading_level = 4
    else:
        reading_level = 5
        
    # Calculate other metrics using simple tokenization
    words = simple_tokenize(text)
    word_count = sum(1 for token in words if token.isalpha())
    
    # Avoid division by zero
    if word_count == 0:
        return {
            'reading_level': 1,
            'flesch_reading_ease': 100,
            'flesch_kincaid_grade': 0,
            'smog_index': 0,
            'avg_word_length': 0,
            'avg_sentence_length': 0,
            'vocabulary_richness': 0,
            'word_count': 0,
            'sentence_count': 0
        }
    
    avg_word_length = sum(len(token) for token in words if token.isalpha()) / word_count if word_count else 0
    
    sentences = simple_sent_tokenize(text)
    sentence_count = len(sentences)
    if sentence_count == 0:
        avg_sentence_length = 0
    else:
        avg_sentence_length = word_count / sentence_count
    
    # Extract vocabulary richness
    unique_words = set(words)
    if not words:
        vocabulary_richness = 0
    else:
        vocabulary_richness = len(unique_words) / len(words)
    
    return {
        'reading_level': reading_level,
        'flesch_reading_ease': flesch_reading_ease,
        'flesch_kincaid_grade': flesch_kincaid_grade,
        'smog_index': smog_index,
        'avg_word_length': avg_word_length,
        'avg_sentence_length': avg_sentence_length,
        'vocabulary_richness': vocabulary_richness,
        'word_count': word_count,
        'sentence_count': sentence_count
    }

def extract_topics(text, n=5):
    """Extract main topics from text using simple frequency"""
    words = simple_tokenize(text)
    
    # Extract nouns, excluding stopwords (simplified approach)
    content_words = [word.lower() for word in words 
                    if word.isalpha() and word.lower() not in stop_words 
                    and len(word) > 3]
    
    # Count and return most common
    from collections import Counter
    word_counts = Counter(content_words)
    common_topics = [item[0] for item in word_counts.most_common(n)]
    return common_topics

def text_to_reading_level(text):
    """Convert text to a numeric reading level"""
    analysis = analyze_text_complexity(text)
    return analysis['reading_level']

def get_age_recommendation(reading_level):
    """Convert reading level to age recommendation"""
    if reading_level <= 1:
        return "5-6"
    elif reading_level <= 2:
        return "6-8"
    elif reading_level <= 3:
        return "8-10"
    elif reading_level <= 4:
        return "10-12"
    else:
        return "12+"

if __name__ == "__main__":
    # Test function
    sample_text = "The cat sat on the mat. It was happy and purring loudly."
    print(analyze_text_complexity(sample_text))
    print(extract_topics(sample_text))