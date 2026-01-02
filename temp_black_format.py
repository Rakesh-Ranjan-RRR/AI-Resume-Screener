import streamlit as st
from PyPDF2 import PdfReader
import re

st.set_page_config(page_title="AI Resume Screener", layout="wide")

# ================= SKILL DATABASE =================
SKILLS_DB = {
    "python", "machine learning", "deep learning", "sql", "nlp",
    "data science", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "aws", "docker", "kubernetes",
    "api", "automation", "n8n", "make.com", "zoho",
    "ai", "ml", "cloud", "computer vision"
}

# ================= FUNCTIONS =================
def clean_text(text):
    return re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())

def extract_skills(text):
    text = clean_text(text)
    return {skill for skill in SKILLS_DB if skill in text}

def extract_years(text):
    matches = re.findall(r"(\d+)\s*\+?\s*years?", text.lower())
    if matches:
        return max(map(int, matches))
    return 0

def ats_score(resume_text, job_text):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    matched = resume_skills & job_skills
    missing = job_skills - resume_skills

    resume_years = extract_years(resume_text)
    required_years = extract_years(job_text)

    skill_score = (len(matched) / max(len(job_skills), 1)) * 100
    experience_bonus = 15 if resume_years >= required_years else -10
    final_score = max(50, min(skill_score + experience_bonus, 95))

    return round(final_score, 2), matched, missing, resume_years, required_years

def read_pdf(file):
    reader = PdfReader(file)
    return " ".join(page.extract_text() or "" for page in reader.pages)

def ai_rewrite_resume(matched, missing, resume_years):
    bullets = []

    for skill in matched:
        bullets.append(
            f"• Applied {skill.title()} in real-world projects to deliver scalable and efficient solutions."
        )

    if resume_years:
        bullets.append(
            f"• Demonstrated {resume_years}+ years of hands-on experience working on production-level systems."
        )

    if missing:
        bullets.append(
            f"• Currently enhancing expertise in {', '.join(list(missing)[:5])} to align with advanced role requirements."
        )

    bullets.append(
        "• Optimized solutions following ATS best practices and industry-aligned keywords."
    )

    return bullets

# ================= UI STYLING =================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #e3f2fd, #e0f7fa);
}
.card {
    background: #e3f2fd;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0px 10px 30px rgba(0, 123, 255, 0.25);
}
textarea {
    background-color: #f5f9ff !important;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.title("🧠 AI Resume Screener")
st.caption("ATS-style AI tool to analyze & rewrite resumes")
st.markdown('</div>', unsafe_allow_html=True)

# ================= INPUTS =================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Upload Resume PDF")
    pdf = st.file_uploader("Upload PDF", type=["pdf"])
    st.subheader("✍️ Paste Resume Text")
    resume_text = st.text_area("Resume Text", height=250)

with col2:
    st.subheader("📌 Paste Job Description")
    job_text = st.text_area("Job Description", height=250)

# ================= ANALYSIS =================
if st.button("🚀 Analyze & Rewrite Resume"):
    if not job_text.strip():
        st.error("Please provide Job Description")
        st.stop()

    if pdf:
        resume_text += " " + read_pdf(pdf)

    if not resume_text.strip():
        st.error("Please provide Resume")
        st.stop()

    score, matched, missing, resume_years, required_years = ats_score(
        resume_text, job_text
    )

    st.markdown("## 📊 ATS Match Score")
    st.progress(int(score))
    st.metric("Match Percentage", f"{score}%")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("❌ Missing Skills")
        for s in missing:
            st.write(f"• {s}")

    with c2:
        st.subheader("✅ Matched Skills")
        for s in matched:
            st.write(f"• {s}")

    st.subheader("📅 Experience Check")
    if resume_years >= required_years:
        st.success(f"Experience OK ({resume_years} / {required_years} years)")
    else:
        st.error(f"Experience Gap ({resume_years} / {required_years} years)")

    # ================= AI RESUME REWRITE =================
    st.subheader("🤖 AI-Generated ATS Resume Rewrite")

    rewritten = ai_rewrite_resume(matched, missing, resume_years)

    rewrite_text = "\n".join(rewritten)
    st.text_area("Optimized Resume Points (Copy-Paste Ready)", rewrite_text, height=220)

    st.success("✔ Resume rewritten using ATS keywords and experience logic")
