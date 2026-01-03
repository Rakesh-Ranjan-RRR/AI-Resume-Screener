import streamlit as st
import re
from collections import Counter
import pdfplumber

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Resume Screener", layout="wide")

# ---------------- STYLES ----------------
st.markdown("""
<style>
body {
    background-color: #eef7ff;
}
.main {
    background-color: #eef7ff;
}
.block {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}
h1 {
    color: #0f172a;
}
textarea {
    background-color: #f8fafc !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="block">
<h1>🧠 AI Resume Screener</h1>
<p>ATS-style AI tool to compare resumes with job descriptions</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------------- PDF READER ----------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# ---------------- SKILL LIST (REAL SKILLS ONLY) ----------------
TECH_SKILLS = [
    "python","machine learning","deep learning","nlp","sql","tensorflow",
    "pytorch","scikit-learn","pandas","numpy","data analysis","automation",
    "aws","azure","gcp","docker","kubernetes","api","flask","fastapi",
    "llm","openai","langchain","vector database","pinecone","faiss",
    "airflow","etl","power bi","tableau"
]

# ---------------- EXPERIENCE EXTRACTOR ----------------
def extract_experience(text):
    matches = re.findall(r'(\d+)\s*\+?\s*years?', text.lower())
    return max(map(int, matches)) if matches else 0

# ---------------- TEXT CLEANER ----------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return text

# ---------------- UI INPUTS ----------------
left, right = st.columns(2)

with left:
    st.markdown("### 📄 Upload Resume (PDF)")
    resume_file = st.file_uploader("Upload PDF", type=["pdf"])
    st.markdown("### ✍️ Paste Resume Text")
    resume_text = st.text_area("Resume Text", height=220)

with right:
    st.markdown("### 📌 Paste Job Description")
    job_text = st.text_area("Job Description", height=480)

# ---------------- ANALYZE ----------------
if st.button("🚀 Analyze Resume"):
    if not job_text or (not resume_text and not resume_file):
        st.warning("Please provide resume and job description.")
    else:
        if resume_file:
            resume_text += read_pdf(resume_file)

        resume_text = clean_text(resume_text)
        job_text = clean_text(job_text)

        resume_exp = extract_experience(resume_text)
        job_exp = extract_experience(job_text)

        resume_skills = set(skill for skill in TECH_SKILLS if skill in resume_text)
        job_skills = set(skill for skill in TECH_SKILLS if skill in job_text)

        matched = resume_skills & job_skills
        missing = job_skills - resume_skills

        # -------- MATCH SCORE LOGIC (FIXED) --------
        skill_score = (len(matched) / max(len(job_skills), 1)) * 70
        exp_score = 30 if resume_exp >= job_exp else (resume_exp / max(job_exp,1)) * 30
        final_score = round(skill_score + exp_score, 2)

        st.markdown("---")
        st.markdown(f"## 🎯 Resume Match Score: **{final_score}%**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ❌ Missing Skills")
            for s in sorted(missing):
                st.write("•", s)

        with col2:
            st.markdown("### ✅ Matched Skills")
            for s in sorted(matched):
                st.write("•", s)

        st.markdown("### 📊 Experience Check")
        if resume_exp >= job_exp:
            st.success(f"Experience requirement met ({resume_exp} years)")
        else:
            st.error(f"Experience gap: Resume {resume_exp} yrs | Required {job_exp} yrs")

        st.markdown("### 🤖 AI Resume Suggestions")
        if missing:
            st.write("• Add missing technical skills from job description.")
        if resume_exp < job_exp:
            st.write("• Highlight relevant experience clearly.")
        st.write("• Use exact keywords from job description.")

