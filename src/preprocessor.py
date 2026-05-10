"""
Text Preprocessing Module

This module handles cleaning and normalizing text extracted from resumes.
Prepares text for NLP analysis and comparison.
"""

import re
import string
from typing import List, Set


def clean_text(text: str) -> str:
    """
    Clean and normalize text for analysis.
    
    Performs:
    - Lowercase conversion
    - Remove special characters (keep alphanumeric and spaces)
    - Remove extra whitespace
    - Remove email addresses (privacy)
    - Remove phone numbers (privacy)
    - Remove URLs
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', ' ', text)
    
    # Remove phone numbers (various formats)
    text = re.sub(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}', ' ', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', ' ', text)
    text = re.sub(r'www\.\S+', ' ', text)
    
    # Remove special characters, keep letters, numbers, spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


def tokenize(text: str) -> List[str]:
    """
    Split text into individual words (tokens).
    
    Args:
        text: Text to tokenize
        
    Returns:
        List of words
    """
    if not text:
        return []
    
    # Simple whitespace tokenization
    tokens = text.split()
    
    # Remove very short tokens (likely noise)
    tokens = [token for token in tokens if len(token) > 1]
    
    return tokens


def remove_stopwords(tokens: List[str], custom_stopwords: Set[str] = None) -> List[str]:
    """
    Remove common English stopwords from token list.
    
    Args:
        tokens: List of words
        custom_stopwords: Additional stopwords to remove
        
    Returns:
        Filtered list of words
    """
    # Common English stopwords
    default_stopwords = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'it', 'its', 'this', 'that', 'these', 'those', 'i', 'me', 'my', 'we',
        'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her', 'they', 'them',
        'their', 'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how',
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'not', 'only', 'same', 'so', 'than', 'too', 'very', 'just',
        'also', 'now', 'here', 'there', 'then', 'once', 'if', 'as', 'while',
        'about', 'against', 'between', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
        'again', 'further', 'any', 'etc', 'ie', 'eg'
    }
    
    stopwords = default_stopwords.copy()
    if custom_stopwords:
        stopwords.update(custom_stopwords)
    
    return [token for token in tokens if token.lower() not in stopwords]


def preprocess_text(text: str, remove_stops: bool = True) -> str:
    """
    Full preprocessing pipeline for text.
    
    Args:
        text: Raw text to process
        remove_stops: Whether to remove stopwords
        
    Returns:
        Preprocessed text string
    """
    # Clean the text
    cleaned = clean_text(text)
    
    # Tokenize
    tokens = tokenize(cleaned)
    
    # Optionally remove stopwords
    if remove_stops:
        tokens = remove_stopwords(tokens)
    
    # Rejoin tokens
    return ' '.join(tokens)


def extract_skills_from_text(text: str, skill_list: List[str]) -> List[str]:
    """
    Extract skills mentioned in text from a predefined skill list.
    
    Uses case-insensitive matching and handles multi-word skills.
    
    Args:
        text: Text to search
        skill_list: List of skills to look for
        
    Returns:
        List of found skills
    """
    if not text or not skill_list:
        return []
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_list:
        skill_lower = skill.lower().strip()
        
        # Check if skill appears in text
        # Use word boundary matching for single words
        if ' ' in skill_lower:
            # Multi-word skill - simple substring match
            if skill_lower in text_lower:
                found_skills.append(skill)
        else:
            # Single word - use word boundary to avoid partial matches
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
    
    return found_skills


def get_skill_match_percentage(found_skills: List[str], required_skills: List[str]) -> float:
    """
    Calculate what percentage of required skills were found.
    
    Args:
        found_skills: Skills found in resume
        required_skills: Skills required for the job
        
    Returns:
        Percentage (0-100)
    """
    if not required_skills:
        return 0.0
    
    matched = len(set(s.lower() for s in found_skills) & 
                  set(s.lower() for s in required_skills))
    
    return (matched / len(required_skills)) * 100


if __name__ == "__main__":
    # Test preprocessing
    sample_text = """
    John Doe - Software Engineer
    Email: john.doe@email.com | Phone: +1-555-123-4567
    
    Skills: Python, JavaScript, SQL, Machine Learning, React
    
    Experience with data analysis and building REST APIs.
    """
    
    print("Original text:")
    print(sample_text)
    print("\nProcessed text:")
    print(preprocess_text(sample_text))
    
    skills = ["Python", "JavaScript", "SQL", "Machine Learning", "Java", "C++"]
    found = extract_skills_from_text(sample_text, skills)
    print(f"\nFound skills: {found}")
