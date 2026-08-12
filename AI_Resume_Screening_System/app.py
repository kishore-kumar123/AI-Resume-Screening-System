from PyPDF2 import PdfReader
import streamlit as st
from reportlab.pdfgen import canvas
import io

st.set_page_config(page_title="AI Resume Screening System", layout="wide")

# ---------------------------------------------------------
# SKILLS + SYNONYMS
# ---------------------------------------------------------
# Each key is the "official" skill name.
# The value is a list of alternate words/abbreviations that count as a match.
SKILL_SYNONYMS = {
    "Python": ["python"],
    "Java": ["java"],
    "SQL": ["sql", "mysql", "postgresql", "postgres", "sqlite", "mssql"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Machine Learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "AI": ["ai", "artificial intelligence"],
    "Deep Learning": ["deep learning", "dl", "neural network", "neural networks", "cnn", "rnn"],
    "Data Analysis": ["data analysis", "data analytics", "pandas", "numpy"],
    "JavaScript": ["javascript", "js", "node.js", "nodejs", "react", "reactjs"],
    "NLP": ["nlp", "natural language processing"],
    "Git": ["git", "github", "version control"],
    "Cloud": ["cloud", "aws", "azure", "gcp", "google cloud"],
}

REQUIRED_SKILLS = ["Python", "SQL", "AI", "Machine Learning", "HTML", "CSS"]

SECTIONS = {
    "Education": ["education"],
    "Skills": ["skills"],
    "Projects": ["project", "projects"],
    "Experience": ["experience", "work experience"],
    "Certifications": ["certification", "certifications", "certificate"],
}


def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text


def find_skills(text):
    text_lower = text.lower()
    found = []
    for skill, synonyms in SKILL_SYNONYMS.items():
        for word in synonyms:
            if word in text_lower:
                found.append(skill)
                break
    return found


def find_sections(text):
    text_lower = text.lower()
    result = {}
    for section, keywords in SECTIONS.items():
        result[section] = any(kw in text_lower for kw in keywords)
    return result


def analyze_resume(uploaded_file):
    text = extract_text_from_pdf(uploaded_file)
    found_skills = find_skills(text)

    score = sum(1 for skill in found_skills if skill in REQUIRED_SKILLS)
    ats_score = (score / len(REQUIRED_SKILLS)) * 100

    missing_skills = [s for s in REQUIRED_SKILLS if s not in found_skills]
    sections_found = find_sections(text)

    if ats_score >= 80:
        strength = "Strong Resume"
        status = "Shortlisted"
    elif ats_score >= 60:
        strength = "Average Resume"
        status = "Under Review"
    else:
        strength = "Weak Resume"
        status = "Needs Improvement"

    if score >= 5:
        role = "AI Engineer / Python Developer"
    elif score >= 3:
        role = "Web Developer / Software Developer"
    else:
        role = "Learn more skills and improve your resume"

    return {
        "name": uploaded_file.name,
        "text": text,
        "found_skills": found_skills,
        "missing_skills": missing_skills,
        "score": score,
        "ats_score": ats_score,
        "strength": strength,
        "status": status,
        "role": role,
        "sections": sections_found,
    }


def make_pdf_report(result):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer)

    c.drawString(100, 800, "AI Resume Screening Report")
    c.drawString(100, 780, f"Resume: {result['name']}")
    c.drawString(100, 760, f"ATS Score: {result['ats_score']:.0f}%")
    c.drawString(100, 740, f"Status: {result['status']}")
    c.drawString(100, 720, f"Recommended Role: {result['role']}")

    y = 690
    c.drawString(100, y, "Skills Found:")
    y -= 20
    for skill in result["found_skills"]:
        c.drawString(120, y, f"- {skill}")
        y -= 18

    y -= 10
    c.drawString(100, y, "Missing Skills:")
    y -= 20
    if result["missing_skills"]:
        for skill in result["missing_skills"]:
            c.drawString(120, y, f"- {skill}")
            y -= 18
    else:
        c.drawString(120, y, "None")

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.header("Required Skills")
    for skill in REQUIRED_SKILLS:
        st.write(f"• {skill}")

    st.divider()
    st.header("All Tracked Skills")
    for skill in SKILL_SYNONYMS.keys():
        st.write(f"• {skill}")

    st.divider()
    st.caption("Synonyms are matched too — e.g. 'ML' counts as Machine Learning, 'JS' counts as JavaScript.")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
st.title("AI Resume Screening System")
st.write("Upload one or more resumes to screen, score, and compare candidates.")

uploaded_files = st.file_uploader(
    "Upload Resume(s) (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    results = [analyze_resume(f) for f in uploaded_files]

    # -------- Comparison table if multiple resumes --------
    if len(results) > 1:
        st.subheader("Candidate Comparison")

        table_data = {
            "Resume": [r["name"] for r in results],
            "ATS Score (%)": [round(r["ats_score"]) for r in results],
            "Skills Matched": [r["score"] for r in results],
            "Status": [r["status"] for r in results],
            "Recommended Role": [r["role"] for r in results],
        }
        st.dataframe(table_data, use_container_width=True)

        best = max(results, key=lambda r: r["ats_score"])
        st.success(f"Top Candidate: {best['name']} ({best['ats_score']:.0f}% ATS match)")

        st.divider()

    # -------- Detailed view per resume --------
    for result in results:
        st.header(result["name"])

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Extracted Skills")
            st.write(result["found_skills"] if result["found_skills"] else "No matching skills found.")

            st.subheader("Missing Skills")
            if result["missing_skills"]:
                st.warning(result["missing_skills"])
            else:
                st.success("No Missing Skills! Excellent Resume.")

            st.subheader("Job Recommendation")
            if result["score"] >= 5:
                st.success(f"Recommended Role: {result['role']}")
            elif result["score"] >= 3:
                st.info(f"Recommended Role: {result['role']}")
            else:
                st.warning(result["role"])

        with col2:
            st.subheader("ATS Score")
            st.progress(int(result["ats_score"]))
            st.write(f"{result['ats_score']:.0f}% match ({result['score']}/{len(REQUIRED_SKILLS)} required skills)")

            if result["strength"] == "Strong Resume":
                st.success(result["strength"])
            elif result["strength"] == "Average Resume":
                st.info(result["strength"])
            else:
                st.error(result["strength"])

            st.subheader("Candidate Status")
            if result["status"] == "Shortlisted":
                st.success(f"Status: {result['status']}")
            elif result["status"] == "Under Review":
                st.warning(f"Status: {result['status']}")
            else:
                st.error(f"Status: {result['status']}")

        st.subheader("Resume Sections Detected")
        section_cols = st.columns(len(SECTIONS))
        for i, (section, found) in enumerate(result["sections"].items()):
            with section_cols[i]:
                if found:
                    st.success(section)
                else:
                    st.warning(section)

        with st.expander("View Extracted Resume Text"):
            st.write(result["text"])

        pdf_buffer = make_pdf_report(result)
        st.download_button(
            label=f"Download Report PDF - {result['name']}",
            data=pdf_buffer,
            file_name=f"Report_{result['name'].replace('.pdf', '')}.pdf",
            mime="application/pdf",
            key=f"download_{result['name']}"
        )

        st.divider()

else:
    st.info("Please upload one or more PDF resumes to continue.")
