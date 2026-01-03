import streamlit as st
import nltk
import pdfplumber
from PyPDF2 import PdfReader
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("stopwords")
from nltk.corpus import stopwords

st.set_page_config(page_title="AI Resume Screener", layout="wide")

# ---------- UI ----------
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #e8f2ff, #f5fbff);
    }
    .header {
        background: linear-gradient(135deg, #b6dbff, #d9ecff);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="header">
        <h1>🧠 AI Resume Screener</h1>
        <p>ATS-style resume vs job description matcher</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- INPUT ----------
col1, col2 = st.columns(2)

with col1:
    resume_text = st.text_area("📄 Paste Resume Text", height=250)
    uploaded_pdf = st.file_uploader("Upload Resume PDF (optional)", type=["pdf"])

with col2:
    jd_text = st.text_area("📌 Paste Job Description", height=250)

# ---------- PDF EXTRACTION ----------
def extract_pdf_text(pdf_file):
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

if uploaded_pdf:
    resume_text = extract_pdf_text(uploaded_pdf)

# ---------- CLEAN TEXT ----------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    stop_words = set(stopwords.words("english"))
    return " ".join([w for w in text.split() if w not in stop_words])

# ---------- ANALYZE ----------
if st.button("🚀 Analyze Resume"):
    if resume_text and jd_text:
        resume_clean = clean_text(resume_text)
        jd_clean = clean_text(jd_text)

        vectorizer = TfidfVectorizer(ngram_range=(1,2))
        tfidf = vectorizer.fit_transform([resume_clean, jd_clean])

        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        match_percent = round(score * 100, 2)

        resume_words = set(resume_clean.split())
        jd_words = set(jd_clean.split())

        matched = sorted(resume_words & jd_words)
        missing = sorted(jd_words - resume_words)

        st.subheader(f"✅ Resume Match Score: {match_percent}%")
        st.progress(match_percent / 100)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("### ❌ Missing Skills")
            st.write(missing[:20])

        with col4:
            st.markdown("### ✅ Matched Skills")
            st.write(matched[:20])

        st.markdown("### 🤖 AI Resume Suggestions")
        if match_percent < 50:
            st.info("Add missing keywords directly into skills & experience sections.")
        elif match_percent < 75:
            st.info("Optimize wording to better match job description keywords.")
        else:
            st.success("Your resume is ATS optimized!")

    else:
        st.warning("Please provide both Resume and Job Description")
