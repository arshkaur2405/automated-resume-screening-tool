"""
Utility Functions Module

Helper functions for file operations, reporting, and general utilities.
"""

import os
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


def get_all_resume_files(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Get all resume files from a directory.
    
    Args:
        directory: Path to the resumes folder
        extensions: List of file extensions to include
        
    Returns:
        List of file paths
    """
    if extensions is None:
        extensions = ['.pdf', '.docx', '.doc', '.txt']
    
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    resume_files = []
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # Check if it's a file with supported extension
        if os.path.isfile(file_path):
            ext = Path(filename).suffix.lower()
            if ext in extensions:
                resume_files.append(file_path)
    
    return sorted(resume_files)


def load_job_description(file_path: str) -> str:
    """
    Load job description from a text file.
    
    Args:
        file_path: Path to the job description file
        
    Returns:
        Job description text
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Job description file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def load_required_skills(file_path: str) -> List[str]:
    """
    Load required skills from a text file (one skill per line).
    
    Args:
        file_path: Path to the skills file
        
    Returns:
        List of skills
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Skills file not found: {file_path}")
    
    skills = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            skill = line.strip()
            if skill and not skill.startswith('#'):  # Ignore empty lines and comments
                skills.append(skill)
    
    return skills


def export_results_to_csv(
    results: List[Dict],
    output_path: str,
    fieldnames: List[str] = None
) -> str:
    """
    Export screening results to a CSV file.
    
    Args:
        results: List of result dictionaries
        output_path: Path for the output CSV file
        fieldnames: Column names (auto-detected if not provided)
        
    Returns:
        Path to the created file
    """
    if not results:
        raise ValueError("No results to export")
    
    # Auto-detect fieldnames from first result
    if fieldnames is None:
        fieldnames = list(results[0].keys())
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    return output_path


def generate_summary_report(results: List[Dict], threshold: float = 60.0) -> str:
    """
    Generate a text summary of screening results.
    
    Args:
        results: List of screening results
        threshold: Shortlist threshold used
        
    Returns:
        Formatted summary string
    """
    total = len(results)
    shortlisted = sum(1 for r in results if r.get('status') == 'Shortlisted')
    rejected = total - shortlisted
    
    if results:
        avg_score = sum(r.get('final_score', 0) for r in results) / total
        top_score = max(r.get('final_score', 0) for r in results)
        lowest_score = min(r.get('final_score', 0) for r in results)
    else:
        avg_score = top_score = lowest_score = 0
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║           RESUME SCREENING SUMMARY REPORT                    ║
╠══════════════════════════════════════════════════════════════╣
║  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                         ║
╠══════════════════════════════════════════════════════════════╣
║  STATISTICS                                                  ║
║  ──────────────────────────────────────────────────────────  ║
║  Total Resumes Processed:  {total:<6}                            ║
║  Shortlisted Candidates:   {shortlisted:<6} ({shortlisted/total*100 if total else 0:.1f}%)                     ║
║  Rejected Candidates:      {rejected:<6} ({rejected/total*100 if total else 0:.1f}%)                     ║
║  ──────────────────────────────────────────────────────────  ║
║  Shortlist Threshold:      {threshold:.1f}%                            ║
║  Average Score:            {avg_score:.2f}%                           ║
║  Highest Score:            {top_score:.2f}%                           ║
║  Lowest Score:             {lowest_score:.2f}%                           ║
╚══════════════════════════════════════════════════════════════╝
"""
    return report


def print_results_table(results: List[Dict]) -> None:
    """
    Print results in a formatted table.
    
    Args:
        results: List of screening results
    """
    if not results:
        print("No results to display.")
        return
    
    # Header
    print("\n" + "="*85)
    print(f"{'Rank':<6}{'Candidate Name':<25}{'Score':<12}{'Skills Match':<15}{'Status':<12}")
    print("="*85)
    
    # Rows
    for r in results:
        rank = r.get('rank', '-')
        name = r.get('candidate_name', 'Unknown')[:24]
        score = f"{r.get('final_score', 0):.2f}%"
        skills = f"{r.get('skill_match_percent', 0):.1f}%"
        status = r.get('status', 'Unknown')
        
        # Color coding for status (works in most terminals)
        if status == 'Shortlisted':
            status_display = f"\033[92m{status}\033[0m"  # Green
        else:
            status_display = f"\033[91m{status}\033[0m"  # Red
        
        print(f"{rank:<6}{name:<25}{score:<12}{skills:<15}{status_display}")
    
    print("="*85 + "\n")


def create_sample_data(data_dir: str) -> None:
    """
    Create sample job description and skills files for testing.
    
    Args:
        data_dir: Directory to create sample files in
    """
    os.makedirs(data_dir, exist_ok=True)
    
    # Sample job description
    job_desc = """Python Developer - Machine Learning

We are looking for a skilled Python Developer with experience in machine learning 
and data analysis to join our growing team.

Requirements:
- 2+ years of experience with Python programming
- Strong knowledge of machine learning frameworks (scikit-learn, TensorFlow, or PyTorch)
- Experience with data analysis using Pandas and NumPy
- Familiarity with SQL databases (PostgreSQL, MySQL)
- Understanding of RESTful APIs
- Experience with version control (Git)
- Good communication skills

Nice to have:
- Experience with cloud platforms (AWS, GCP, Azure)
- Knowledge of Docker and containerization
- Experience with natural language processing
- Familiarity with Agile methodologies

Responsibilities:
- Develop and maintain machine learning models
- Analyze large datasets to extract insights
- Build data pipelines and ETL processes
- Collaborate with cross-functional teams
- Write clean, maintainable code with proper documentation
"""
    
    with open(os.path.join(data_dir, 'job_description.txt'), 'w') as f:
        f.write(job_desc)
    
    # Sample required skills
    skills = """# Required Skills (one per line)
Python
Machine Learning
Pandas
NumPy
SQL
scikit-learn
Git
Data Analysis
REST API
TensorFlow
Communication
"""
    
    with open(os.path.join(data_dir, 'required_skills.txt'), 'w') as f:
        f.write(skills)
    
    print(f"Sample data files created in: {data_dir}")


if __name__ == "__main__":
    # Test utilities
    print("Utility Functions Module")
    create_sample_data("./data")
