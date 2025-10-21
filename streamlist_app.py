import os
import json
import streamlit as st
from dotenv import load_dotenv

from crew_app.file_tools.file_loader import detect_and_extract
from crew_app.crew import run_pipeline
from crew_app.utils import txt_to_docx_bytes

# Load env
load_dotenv()
st.set_page_config(page_title="ATS Resume Agent (CrewAI)", page_icon="📝", layout="wide")

st.title("🤖 ATS-Optimized Resume Agent (CrewAI + OpenAI)")
st.caption("Upload your resume (.pdf or .docx), target a role, and get an ATS-friendly version with scores & quick wins!")

# Settings Sidebar
with st.sidebar:
    st.subheader("OpenAI Settings")
    st.text_input("Model:", value="gpt-4o-mini", disabled=True)
    st.write("✅ API key loaded:  Working OpenAI key")

# Inputs
coll, colR = st.columns([1,1])
with coll:
    up = st.file_uploader("Upload Resume (.pdf or .docx preferred)", type=["pdf", "docx", "txt"])
with colR:
    # ... rest of the code is not fully visible
    job_title = st.text_input("Target Job Title (e.g., 'Machine Learning Engineer')")
    job_desc = st.text_area("Paste Job Description", height=220, placeholder="Paste JD here...")

run_btn = st.button("Run ATS Agent")

tabs = st.tabs(["Cleaned Resume", "Rewritten (ATS-optimized)", "Final (Refined Bullets)", "ATS Evaluation"])

if run_btn:
    if up is None:
        st.error("Please upload a resume file.")
    elif not job_title or not job_desc.strip():
        st.error("Please provide a target job title and job description.")
    else:
        ext, raw_text = detect_and_extract(up.name, up.read())
        # ... rest of the code is not fully visible
        if not raw_text.strip():
            st.error("Could not extract any text from the file.")
        else:
            with st.spinner("Running Crew agents..."):
                cleaned, rewritten, final_resume, evaluation = run_pipeline(
                    raw_resume_text=raw_text,
                    job_title=job_title.strip(),
                    job_description=job_desc.strip()
                )

            with tabs[0]:
                st.subheader("Cleaned Resume (plain text)")
                # ... rest of the code is not fully visible
                st.code(cleaned, language="markdown")
                st.download_button(
                    "Download cleaned.txt",
                    data=cleaned.encode("utf-8"),
                    file_name="cleaned_resume.txt",
                    mime="text/plain"
                )

            with tabs[1]:
                st.subheader("Rewritten Resume (ATS-optimized)")
                st.code(rewritten, language="markdown")
                st.download_button(
                    "Download rewritten.txt",
                    data=rewritten.encode("utf-8"),
                    file_name="rewritten_resume.txt",
                    mime="text/plain"
                )

            with tabs[2]:
                st.subheader("Final Resume (Enhanced Bullet Points)")
                st.code(final_resume, language="markdown")
                
                # DOCX Download for Final Resume
                docx_bytes = txt_to_docx_bytes(final_resume)
                st.download_button(
                    "Download Final Resume (DOCX)",
                    data=docx_bytes,
                    file_name="final_ats_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            with tabs[3]:
                st.subheader("ATS Evaluation")
                try:
                    # Parse the JSON string output from the evaluation agent
                    eval_data = json.loads(evaluation)
                    
                    # Display Overall Score
                    st.metric(
                        "Overall ATS Score (0-100)", 
                        eval_data.get("overall_score", "N/A"),
                        help="Score based on keywords, structure, metrics, verbs, and format."
                    )
                    
                    # Display Breakdown and Recommendations
                    if "breakdown" in eval_data:
                        st.subheader("Breakdown (1-5 Rating)")
                        st.json(eval_data["breakdown"])
                    
                    if "recommendations" in eval_data:
                        st.subheader("Quick Win Recommendations")
                        st.markdown(eval_data["recommendations"])

                except json.JSONDecodeError:
                    st.error("Error: Could not parse evaluation output. Raw text below:")
                    st.code(evaluation)