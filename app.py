import streamlit as st
import pdfplumber
import docx
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="ATS Resume Screening Tool",
    layout="wide"
)

st.title("📄 Automated Resume Screening Tool (ATS Simulation)")
st.markdown("Upload resumes (PDF, DOCX, TXT) and match them with job description using NLP (TF-IDF + Cosine Similarity).")

# ----------------------------
# FILE EXTRACTION FUNCTIONS
# ----------------------------

def extract_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_txt(file):
    return file.read().decode("utf-8", errors="ignore")


# ----------------------------
# SIDEBAR INPUT
# ----------------------------

st.sidebar.header("📤 Upload Section")

uploaded_files = st.sidebar.file_uploader(
    "Upload Resumes (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

job_description = st.text_area(
    "📝 Enter Job Description",
    height=200,
    placeholder="Enter required skills, experience, tools..."
)

threshold = st.sidebar.slider("Shortlisting Threshold (%)", 0, 100, 50)

# ----------------------------
# START BUTTON
# ----------------------------

if st.button("🚀 Start Screening"):

    if not uploaded_files:
        st.warning("Please upload at least one resume.")
        st.stop()

    if job_description.strip() == "":
        st.warning("Please enter job description.")
        st.stop()

    resumes = []
    names = []

    # ----------------------------
    # EXTRACT TEXT FROM FILES
    # ----------------------------
    for file in uploaded_files:

        if file.name.endswith(".pdf"):
            text = extract_pdf(file)

        elif file.name.endswith(".docx"):
            text = extract_docx(file)

        elif file.name.endswith(".txt"):
            text = extract_txt(file)

        else:
            continue

        resumes.append(text)
        names.append(file.name)

    # ----------------------------
    # TF-IDF + COSINE SIMILARITY
    # ----------------------------
    documents = resumes + [job_description]

    tfidf = TfidfVectorizer(stop_words="english")
    matrix = tfidf.fit_transform(documents)

    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    # ----------------------------
    # DATAFRAME
    # ----------------------------
    df = pd.DataFrame({
        "Resume": names,
        "Similarity Score (%)": scores * 100
    })

    df = df.sort_values(by="Similarity Score (%)", ascending=False)

    df["Status"] = df["Similarity Score (%)"].apply(
        lambda x: "Shortlisted" if x >= threshold else "Rejected"
    )

    # ----------------------------
    # RESULTS
    # ----------------------------
    st.subheader("📊 Ranking Results")
    st.dataframe(df, use_container_width=True)

    # ----------------------------
    # SHORTLISTED / REJECTED
    # ----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.success("✅ Shortlisted Candidates")
        st.dataframe(df[df["Status"] == "Shortlisted"], use_container_width=True)

    with col2:
        st.error("❌ Rejected Candidates")
        st.dataframe(df[df["Status"] == "Rejected"], use_container_width=True)

    # ----------------------------
    # VISUALIZATION
    # ----------------------------
    st.subheader("📈 Score Visualization")
    st.bar_chart(df.set_index("Resume")["Similarity Score (%)"])

    # ----------------------------
    # DOWNLOAD REPORT
    # ----------------------------
    csv = df.to_csv(index=False).encode("utf-8")

    file_name = f"resume_screening_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    st.download_button(
        "📥 Download Report CSV",
        data=csv,
        file_name=file_name,
        mime="text/csv"
    )

    st.success("Screening Completed Successfully 🚀")
    # ...
    