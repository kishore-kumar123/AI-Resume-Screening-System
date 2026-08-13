from PyPDF2 import PdfReader
from docx import Document
import streamlit as st
from reportlab.pdfgen import canvas
import io
import re

st.set_page_config(page_title="AI Resume Screening System", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
</style>
""", unsafe_allow_html=True)
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

# ✅ IMPROVEMENT: More section keywords
SECTIONS = {
    "Education": ["education", "degree", "bachelor", "master", "university"],
    "Skills": ["skills", "technical skills", "competencies", "abilities"],
    "Projects": ["project", "projects", "portfolio", "work"],
    "Experience": ["experience", "work experience", "employment", "job", "role"],
    "Certifications": ["certification", "certifications", "certificate", "certified"],
}


# ✅ IMPROVEMENT: Text cleaning function
def clean_text(text):
    """Clean and normalize resume text"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\-,.]', '', text)
    return text.strip()


# ✅ IMPROVEMENT: PDF extraction with error handling
def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF with error handling"""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return clean_text(text) if text.strip() else None
    except Exception as e:
        st.error(f"❌ Error extracting PDF: {str(e)}")
        return None


# ✅ IMPROVEMENT: DOCX extraction function
def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX with error handling"""
    try:
        doc = Document(uploaded_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return clean_text(text) if text.strip() else None
    except Exception as e:
        st.error(f"❌ Error extracting DOCX: {str(e)}")
        return None


# ✅ IMPROVEMENT: Universal text extraction
def extract_resume_text(uploaded_file):
    """Extract text from PDF or DOCX"""
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    else:
        st.error(f"❌ Unsupported file format: {uploaded_file.type}")
        return None


# ✅ IMPROVEMENT: Find skills with duplicate removal
def find_skills(text):
    """Find all skills in resume"""
    text_lower = text.lower()
    found = []
    for skill, synonyms in SKILL_SYNONYMS.items():
        for word in synonyms:
            if word in text_lower:
                found.append(skill)
                break
    return list(set(found))  # Remove duplicates


def find_sections(text):
    text_lower = text.lower()
    result = {}
    for section, keywords in SECTIONS.items():
        result[section] = any(kw in text_lower for kw in keywords)
    return result


# ✅ IMPROVEMENT: Better ATS score calculation
def calculate_ats_score(found_skills, text, required_skills):
    """Calculate ATS score with weighted criteria"""
    
    # Required skills (50% weight)
    required_matched = sum(1 for skill in found_skills if skill in required_skills)
    required_score = (required_matched / len(required_skills)) * 50
    
    # All skills found (30% weight)
    all_skills_count = len(found_skills)
    all_skills_score = min((all_skills_count / 15) * 30, 30)
    
    # Section completeness (20% weight)
    sections = find_sections(text)
    sections_present = sum(1 for v in sections.values() if v)
    sections_score = (sections_present / len(SECTIONS)) * 20
    
    total_score = required_score + all_skills_score + sections_score
    return min(total_score, 100)


# ✅ IMPROVEMENT: Analyze resume with error handling
def analyze_resume(uploaded_file):
    """Analyze resume and return results"""
    text = extract_resume_text(uploaded_file)
    
    if text is None or text.strip() == "":
        return None
    
    found_skills = find_skills(text)
    ats_score = calculate_ats_score(found_skills, text, REQUIRED_SKILLS)
    
    required_matched = sum(1 for skill in found_skills if skill in REQUIRED_SKILLS)
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

    if required_matched >= 5:
        role = "AI Engineer / ML Developer"
    elif required_matched >= 3:
        role = "Web Developer / Software Developer"
    else:
        role = "Learn more skills and improve your resume"

    return {
        "name": uploaded_file.name,
        "text": text,
        "found_skills": found_skills,
        "missing_skills": missing_skills,
        "score": required_matched,
        "ats_score": ats_score,
        "strength": strength,
        "status": status,
        "role": role,
        "sections": sections_found,
    }


# ✅ IMPROVEMENT: Better PDF report formatting
def make_pdf_report(result):
    """Generate PDF report with better formatting"""
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(600, 800))

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "AI Resume Screening Report")
    
    # Content
    c.setFont("Helvetica", 11)
    c.drawString(50, 720, f"Resume: {result['name']}")
    c.drawString(50, 700, f"ATS Score: {result['ats_score']:.1f}%")
    c.drawString(50, 680, f"Status: {result['status']}")
    c.drawString(50, 660, f"Recommended Role: {result['role']}")

    y = 630
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Skills Found:")
    
    c.setFont("Helvetica", 10)
    y -= 20
    if result["found_skills"]:
        for skill in result["found_skills"]:
            c.drawString(70, y, f"• {skill}")
            y -= 15
    else:
        c.drawString(70, y, "No matching skills found")
        y -= 15

    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Missing Skills:")
    
    c.setFont("Helvetica", 10)
    y -= 20
    if result["missing_skills"]:
        for skill in result["missing_skills"]:
            c.drawString(70, y, f"• {skill}")
            y -= 15
    else:
        c.drawString(70, y, "None - All required skills present!")

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
    st.caption(f"Total: {len(SKILL_SYNONYMS)} skills")
    for skill in SKILL_SYNONYMS.keys():
        st.write(f"• {skill}")

    st.divider()
    st.caption("✨ **NEW:** DOCX format also supported now!\n\nSynonyms are matched too — e.g. 'ML' counts as Machine Learning, 'JS' counts as JavaScript.")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
st.title("AI Resume Screening System")
st.write("Upload one or more resumes (PDF or DOCX) to screen, score, and compare candidates.")

# ✅ IMPROVEMENT: File uploader with DOCX support
uploaded_files = st.file_uploader(
    "Upload Resume(s) (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    help="Supported formats: PDF, DOCX"
)

if uploaded_files:
    # ✅ IMPROVEMENT: Loading indicator
    with st.spinner("🔍 Analyzing resumes..."):
        results = [analyze_resume(f) for f in uploaded_files]
        results = [r for r in results if r is not None]
    
    # ✅ IMPROVEMENT: Error handling
    if not results:
        st.error("❌ Could not process any of the uploaded files. Please check the files and try again.")
    else:
        st.success(f"✅ Successfully processed {len(results)} resume(s)!")
        st.divider()

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
                st.progress(int(result["ats_score"]) / 100)
                st.write(f"{result['ats_score']:.1f}% match ({result['score']}/{len(REQUIRED_SKILLS)} required skills)")

                # ✅ IMPROVEMENT: Score breakdown
                st.markdown(f"""
                **Score Breakdown:**
                - Required Skills: {result['score']}/{len(REQUIRED_SKILLS)}
                - Total Skills Found: {len(result['found_skills'])}
                - Sections Found: {sum(1 for v in result['sections'].values() if v)}/{len(SECTIONS)}
                """)

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
                file_name=f"Report_{result['name'].replace('.pdf', '').replace('.docx', '')}.pdf",
                mime="application/pdf",
                key=f"download_{result['name']}"
            )

            st.divider()

else:
    st.info("Please upload one or more PDF/DOCX resumes to continue.")
