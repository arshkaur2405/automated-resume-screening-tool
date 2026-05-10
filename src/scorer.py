"""
Resume Scoring Module

This module handles scoring resumes against job descriptions using
TF-IDF vectorization and cosine similarity.
"""

import numpy as np
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ResumeScorer:
    """
    Scores resumes against a job description using TF-IDF and cosine similarity.
    """
    
    def __init__(self):
        """Initialize the scorer with a TF-IDF vectorizer."""
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            max_features=5000,       # Limit vocabulary size
            ngram_range=(1, 2),      # Use unigrams and bigrams
            stop_words='english'     # Remove English stop words
        )
        self.job_description_vector = None
        
    def fit_job_description(self, job_description: str) -> None:
        """
        Fit the vectorizer on the job description.
        
        Args:
            job_description: The job description text
        """
        # Fit and transform the job description
        self.job_description_vector = self.vectorizer.fit_transform([job_description])
        
    def score_resume(self, resume_text: str) -> float:
        """
        Calculate similarity score between a resume and the job description.
        
        Args:
            resume_text: Preprocessed resume text
            
        Returns:
            Similarity score (0-100)
        """
        if self.job_description_vector is None:
            raise ValueError("Must call fit_job_description() first")
        
        if not resume_text or not resume_text.strip():
            return 0.0
        
        # Transform resume using fitted vectorizer
        # Handle vocabulary mismatch by using the same vectorizer
        resume_vector = self.vectorizer.transform([resume_text])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(self.job_description_vector, resume_vector)[0][0]
        
        # Convert to percentage (0-100)
        score = similarity * 100
        
        return round(score, 2)
    
    def score_multiple_resumes(
        self, 
        job_description: str, 
        resumes: Dict[str, str]
    ) -> List[Dict]:
        """
        Score multiple resumes against a job description.
        
        Args:
            job_description: The job description text
            resumes: Dictionary of {candidate_name: resume_text}
            
        Returns:
            List of dictionaries with scoring results
        """
        # Combine job description with all resumes for consistent vectorization
        all_texts = [job_description] + list(resumes.values())
        
        # Fit and transform all texts together
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Job description is first document
        job_vector = tfidf_matrix[0:1]
        
        results = []
        for idx, (name, resume_text) in enumerate(resumes.items(), start=1):
            resume_vector = tfidf_matrix[idx:idx+1]
            
            # Calculate similarity
            similarity = cosine_similarity(job_vector, resume_vector)[0][0]
            score = round(similarity * 100, 2)
            
            results.append({
                'candidate_name': name,
                'similarity_score': score,
                'resume_text_length': len(resume_text)
            })
        
        return results


def calculate_combined_score(
    similarity_score: float, 
    skill_match_percentage: float,
    similarity_weight: float = 0.6,
    skill_weight: float = 0.4
) -> float:
    """
    Calculate a combined score from similarity and skill matching.
    
    Args:
        similarity_score: TF-IDF cosine similarity score (0-100)
        skill_match_percentage: Percentage of required skills found (0-100)
        similarity_weight: Weight for similarity score
        skill_weight: Weight for skill matching
        
    Returns:
        Combined score (0-100)
    """
    if similarity_weight + skill_weight != 1.0:
        # Normalize weights
        total = similarity_weight + skill_weight
        similarity_weight /= total
        skill_weight /= total
    
    combined = (similarity_score * similarity_weight) + (skill_match_percentage * skill_weight)
    return round(combined, 2)


def rank_candidates(
    candidates: List[Dict], 
    score_key: str = 'final_score'
) -> List[Dict]:
    """
    Rank candidates by their scores (highest first).
    
    Args:
        candidates: List of candidate dictionaries
        score_key: Key containing the score to rank by
        
    Returns:
        Sorted list with rank added
    """
    # Sort by score (descending)
    sorted_candidates = sorted(
        candidates, 
        key=lambda x: x.get(score_key, 0), 
        reverse=True
    )
    
    # Add rank
    for idx, candidate in enumerate(sorted_candidates, start=1):
        candidate['rank'] = idx
    
    return sorted_candidates


def apply_shortlist_threshold(
    candidates: List[Dict],
    threshold: float = 60.0,
    score_key: str = 'final_score'
) -> List[Dict]:
    """
    Mark candidates as shortlisted or rejected based on threshold.
    
    Args:
        candidates: List of candidate dictionaries
        threshold: Minimum score to be shortlisted
        score_key: Key containing the score
        
    Returns:
        Candidates with 'status' field added
    """
    for candidate in candidates:
        score = candidate.get(score_key, 0)
        candidate['status'] = 'Shortlisted' if score >= threshold else 'Rejected'
    
    return candidates


if __name__ == "__main__":
    # Test the scorer
    scorer = ResumeScorer()
    
    job_desc = "Looking for Python developer with experience in machine learning, data analysis, and SQL databases."
    
    resumes = {
        "John Doe": "python developer experienced in machine learning sklearn pandas data analysis sql postgresql",
        "Jane Smith": "java developer spring boot microservices docker kubernetes",
        "Alex Kumar": "python sql data scientist machine learning deep learning tensorflow"
    }
    
    results = scorer.score_multiple_resumes(job_desc, resumes)
    
    print("Scoring Results:")
    for result in results:
        print(f"  {result['candidate_name']}: {result['similarity_score']}%")
