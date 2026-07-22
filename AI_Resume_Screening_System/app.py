from PyPDF2 import PdfReader
import streamlit as st

st.set_page_config(page_title="AI Resume Screening System")

st.title("AI Resume Screening System")
st.write("Welcome to the AI Resume Screening System!")
uploaded_file = st.file_uploader(
    "Upload your Resume (PDF)",
    type=["pdf"]
)

if uploaded_file is not None:
    st.success("Resume uploaded successfully!")

    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        text += page.extract_text()

    st.subheader("Resume Text")
    st.write(text)
    skills = ["Python", "Java", "SQL", "HTML", "CSS", "Machine Learning", "AI"]

found_skills = []
skills = [
    "Python",
    "Java",
    "SQL",
    "HTML",
    "CSS",
    "Machine Learning",
    "AI"
]
for skill in skills:
    if skill.lower() in text.lower():
        found_skills.append(skill)

st.subheader("Extracted Skills")
required_skills = ["Python", "SQL", "AI", "Machine Learning", "HTML", "CSS"]

score = 0

for skill in skills:
    if skill in required_skills:
        score += 1

st.subheader("Resume Score")
st.subheader("Job Recommendation")

if score >= 5:
    st.success("Recommended Role: AI Engineer / Python Developer")
elif score >= 3:
    st.info("Recommended Role: Web Developer / Software Developer")
else:
    st.warning("Recommendation: Learn more skills and improve your resume.")
    st.subheader("Missing Skills")

missing_skills = []

for skill in required_skills:
    if skill not in skills:
        missing_skills.append(skill)

if missing_skills:
    st.warning(missing_skills)
else:
    st.success("No Missing Skills! Excellent Resume.")
st.write(f"Score: {score}/{len(required_skills)}")
ats_score = (score / len(required_skills)) * 100

st.subheader("ATS Score")
st.progress(int(ats_score))
st.success(f"ATS Match Score: {ats_score:.0f}%")
st.subheader("Resume Strength")

if ats_score >= 80:
    st.success("Strong Resume")
elif ats_score >= 60:
    st.info("Average Resume")
else:
    st.error("Weak Resume")
st.subheader("Resume Summary")

if ats_score >= 80:
    st.success("Excellent Resume! Your resume is suitable for AI Engineer / Python Developer roles.")
elif ats_score >= 60:
    st.info("Good Resume. Add more relevant skills and projects to improve your ATS score.")
else:
    st.warning("Your resume needs improvement. Add more technical skills, projects, and certifications.")
st.subheader("Resume Strength")
st.subheader("Resume Sections Detection")

sections = {
    "Education": "education",
    "Skills": "skills",
    "Projects": "project",
    "Experience": "experience",
    "Certifications": "certification"
}

for section, keyword in sections.items():
    if keyword.lower() in text.lower():
        st.success(f"✅ {section} Section Found")
    else:
        st.warning(f"❌ {section} Section Missing")
st.subheader("Improvement Suggestions")

if missing_skills:
    for skill in missing_skills:
        st.write(f"• Learn {skill}")
else:
    st.success("Your resume is well optimized. No improvements needed.")
    st.subheader("Candidate Status")

if ats_score >= 80:
    st.success("Status: Shortlisted")
elif ats_score >= 60:
    st.warning("Status: Under Review")
else:
    st.error("Status: Needs Improvement")
    st.subheader("Candidate Status")

if ats_score >= 80:
    st.success("Status: Shortlisted")
elif ats_score >= 60:
    st.warning("Status: Under Review")
else:
    st.error("Status: Needs Improvement")
st.write(found_skills)
from reportlab.pdfgen import canvas
import io

pdf_buffer = io.BytesIO()
c = canvas.Canvas(pdf_buffer)

c.drawString(100, 800, "AI Resume Screening Report")
c.drawString(100, 780, f"ATS Score: {ats_score:.0f}%")

y = 760
for skill in found_skills:
    c.drawString(100, y, f"Skill: {skill}")
    y -= 20

c.save()
pdf_buffer.seek(0)

st.download_button(
    label="📄 Download Report PDF",
    data=pdf_buffer,
    file_name="Resume_Report.pdf",
    mime="application/pdf"
)