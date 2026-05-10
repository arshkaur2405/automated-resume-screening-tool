📄 Automated Resume Screening Tool
🚀 Overview

The Automated Resume Screening Tool is an AI-powered Python project that automates the process of evaluating and shortlisting candidates by matching resumes with a given job description using Natural Language Processing (NLP) techniques.

It acts as a simplified Applicant Tracking System (ATS) that helps HR teams and recruiters save time by automatically analyzing resumes, extracting skills, and ranking candidates based on relevance.

The system supports PDF, DOCX, and TXT resumes, processes text using TF-IDF, and calculates similarity using cosine similarity to generate accurate ranking scores.

A Streamlit-based dashboard is also included for interactive resume upload, visualization, and report generation.

🎯 Problem Statement

Manually screening resumes is:

Time-consuming ⏳
Error-prone ❌
Subjective ⚖️

This project solves these issues by:

Automating resume evaluation
Ranking candidates objectively
Extracting skill-based insights
Reducing HR workload significantly

🧠 How It Works
Upload resumes (PDF / DOCX / TXT)
Enter job description
System extracts and cleans text
TF-IDF converts text into vectors
Cosine similarity measures match score
Candidates are ranked
Shortlisted & rejected lists are generated
Results exported as CSV report

📊 Features
📄 Multi-format resume support (PDF, DOCX, TXT)
🧠 NLP-based text analysis
📊 TF-IDF + Cosine Similarity matching
🏆 Automated ranking system
✅ Shortlisting based on threshold
📈 Interactive Streamlit dashboard
📥 CSV report download
⚡ Fast and scalable processing

🛠️ Tech Stack
Python 🐍
Pandas, NumPy
Scikit-learn (TF-IDF, Cosine Similarity)
pdfplumber
python-docx
Streamlit (UI Dashboard)

📁 Project Structure
Automated-Resume-Screening-Tool/
│
├── data/               # Job description & skills data
├── docs/              # Documentation
├── images/            # Screenshots
├── outputs/           # Generated reports (CSV, TXT)
├── resumes/           # Sample resumes
├── src/               # Core modules (NLP, scoring, utils)
│
├── app.py             # Streamlit dashboard
├── main.py            # Backend pipeline
├── requirements.txt   # Dependencies
├── .gitignore
└── README.md

🚀 How to Run
1️⃣ Install dependencies
pip install -r requirements.txt
2️⃣ Run backend (CLI version)
python main.py
3️⃣ Run Streamlit dashboard
streamlit run app.py
📈 Output Example
Ranked Resume List
Similarity Score (%)
Skill Match Score
Shortlisted Candidates
CSV Report Export

🎯 Learning Outcomes

This project helps in understanding:

NLP (Natural Language Processing)
TF-IDF vectorization
Cosine similarity
Data preprocessing
Automation workflows
Real-world ATS systems

📌 Future Improvements
AI-based semantic matching (BERT)
Email automation for shortlisted candidates
Database integration (MySQL / MongoDB)
Resume keyword highlighting
Login-based HR dashboard
