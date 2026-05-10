"""
Automated Resume Screening Tool
================================

A Python-based solution for screening resumes against job descriptions
using NLP techniques (TF-IDF and Cosine Similarity).

Author: Your Name
Version: 1.0.0
"""

import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.extractor import extract_text, get_candidate_name_from_filename
from src.preprocessor import (
    preprocess_text,
    extract_skills_from_text,
    get_skill_match_percentage
)
from src.scorer import (
    ResumeScorer,
    calculate_combined_score,
    rank_candidates,
    apply_shortlist_threshold
)
from src.utils import (
    get_all_resume_files,
    load_job_description,
    load_required_skills,
    export_results_to_csv,
    generate_summary_report,
    print_results_table,
    create_sample_data
)

# ----------------------------
# BANNER
# ----------------------------
def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║        AUTOMATED RESUME SCREENING TOOL              ║
    ║        Python | NLP | AI Matching System            ║
    ╚══════════════════════════════════════════════════════╝
    """)

# ----------------------------
# MAIN SCREENING FUNCTION
# ----------------------------
def screen_resumes(
    resumes_dir="resumes",
    job_desc_path="data/job_description.txt",
    skills_path="data/required_skills.txt",
    output_dir="outputs",
    threshold=50.0,
    similarity_weight=0.6,
    skill_weight=0.4
):

    print_banner()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting screening...\n")

    # ----------------------------
    # STEP 1: LOAD JOB + SKILLS
    # ----------------------------
    print("📋 Step 1: Loading job description & skills...")

    try:
        job_description = load_job_description(job_desc_path)
    except FileNotFoundError:
        print("⚠ Missing job description. Creating sample data...")
        create_sample_data("data")
        job_description = load_job_description(job_desc_path)

    try:
        required_skills = load_required_skills(skills_path)
    except FileNotFoundError:
        required_skills = []

    print(f"✓ Job loaded ({len(job_description)} chars)")
    print(f"✓ Skills loaded ({len(required_skills)} skills)\n")

    # ----------------------------
    # STEP 2: LOAD RESUMES
    # ----------------------------
    print("📁 Step 2: Loading resumes...")

    resume_files = get_all_resume_files(resumes_dir)

    if not resume_files:
        print("❌ No resumes found!")
        return []

    print(f"✓ Found {len(resume_files)} resumes\n")

    resumes_data = []

    # ----------------------------
    # STEP 3: EXTRACT TEXT
    # ----------------------------
    print("📄 Step 3: Extracting resume text...")

    for file_path in resume_files:

        filename = os.path.basename(file_path)
        candidate_name = get_candidate_name_from_filename(file_path)

        try:
            raw_text = extract_text(file_path)

            if not raw_text.strip():
                continue

            processed_text = preprocess_text(raw_text)

            found_skills = extract_skills_from_text(raw_text, required_skills)
            skill_match = get_skill_match_percentage(found_skills, required_skills)

            resumes_data.append({
                "name": candidate_name,
                "filename": filename,
                "text": processed_text,
                "skills": found_skills,
                "skill_score": skill_match
            })

            print(f"✓ {filename} processed")

        except Exception as e:
            print(f"❌ Error in {filename}: {e}")

    if not resumes_data:
        return []

    print("\n")

    # ----------------------------
    # STEP 4: SIMILARITY SCORE
    # ----------------------------
    print("🔍 Step 4: Calculating similarity scores...")

    job_processed = preprocess_text(job_description)

    scorer = ResumeScorer()

    resume_text_map = {
        r["name"]: r["text"] for r in resumes_data
    }

    similarity_results = scorer.score_multiple_resumes(
        job_processed,
        resume_text_map
    )

    similarity_map = {
        r["candidate_name"]: r["similarity_score"]
        for r in similarity_results
    }

    for r in resumes_data:
        r["similarity"] = similarity_map.get(r["name"], 0)

    # ----------------------------
    # STEP 5: FINAL SCORING
    # ----------------------------
    print("📊 Step 5: Ranking candidates...")

    results = []

    for r in resumes_data:

        final_score = calculate_combined_score(
            similarity_score=r["similarity"],
            skill_match_percentage=r["skill_score"],
            similarity_weight=similarity_weight,
            skill_weight=skill_weight
        )

        results.append({
            "candidate_name": r["name"],
            "filename": r["filename"],
            "similarity_score": r["similarity"],
            "skill_match_percent": r["skill_score"],
            "skills_found": ", ".join(r["skills"]) if r["skills"] else "None",
            "final_score": final_score
        })

    results = rank_candidates(results)
    results = apply_shortlist_threshold(results, threshold)

    # ----------------------------
    # STEP 6: DISPLAY
    # ----------------------------
    print("\n📈 RESULTS:\n")
    print_results_table(results)

    summary = generate_summary_report(results, threshold)
    print(summary)

    # ----------------------------
    # STEP 7: EXPORT
    # ----------------------------
    print("💾 Step 7: Exporting results...")

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = os.path.join(output_dir, f"screening_results_{timestamp}.csv")

    export_results_to_csv(results, csv_path)

    print(f"✓ CSV saved: {csv_path}")

    latest_path = os.path.join(output_dir, "screening_results_latest.csv")

    export_results_to_csv(results, latest_path)

    print(f"✓ Latest saved: {latest_path}")

    # ----------------------------
    # FIXED SUMMARY EXPORT (IMPORTANT FIX)
    # ----------------------------
    summary_path = os.path.join(output_dir, f"summary_report_{timestamp}.txt")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
        f.write("\n\nDETAILED RESULTS:\n")
        f.write("=" * 60 + "\n")

        for r in results:
            f.write(f"\nRank #{r['rank']} - {r['candidate_name']}\n")
            f.write(f"Final Score: {r['final_score']:.2f}%\n")
            f.write(f"Similarity: {r['similarity_score']:.2f}%\n")
            f.write(f"Skill Match: {r['skill_match_percent']:.1f}%\n")
            f.write(f"Skills: {r['skills_found']}\n")
            f.write(f"Status: {r['status']}\n")

    print(f"✓ Summary saved: {summary_path}")

    shortlisted = sum(1 for r in results if r["status"] == "Shortlisted")

    print(f"\n✅ Done! {shortlisted}/{len(results)} shortlisted.\n")

    return results

# ----------------------------
# MAIN
# ----------------------------
def main():

    CONFIG = {
        "resumes_dir": "resumes",
        "job_desc_path": "data/job_description.txt",
        "skills_path": "data/required_skills.txt",
        "output_dir": "outputs",
        "threshold": 50.0,
        "similarity_weight": 0.6,
        "skill_weight": 0.4
    }

    results = screen_resumes(**CONFIG)

    if not results:
        print("⚠ No results generated. Check resumes and data files.")

# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    main()
    # ...