import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF
from docx import Document
import streamlit as st

# ======================================================
# Key Improvements (as comments)
# - Summary Type Selection: The user can choose from six different summary types.
# - Prompt Customization: Each summary type uses a tailored prompt.
# - User Experience: Streamlit provides a clean, interactive UI.
#
# Summary Type Details
# | Option | Summary Type      | Prompt Focus                                              |
# |--------|------------------|-----------------------------------------------------------|
# | 1      | Default summary  | General overview, main points                             |
# | 2      | Article summary  | Title, introduction, main points, supporting details, conclusion |
# | 3      | Project summary  | Purpose, steps, results, implications                     |
# | 4      | Bullet summary   | Key points in bullet format                               |
# | 5      | Research summary | Research question, methodology, results, conclusion       |
# | 6      | Resume summary   | Skills, experience, brief professional profile            |
# ======================================================

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def get_website_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for unwanted in soup.find_all(['script', 'style', 'nav', 'footer']):
            unwanted.decompose()
        text = soup.get_text()
        clean_text = ' '.join(text.split())
        if len(clean_text) < 50:
            return "Error: Website content too short or empty"
        return clean_text
    except requests.exceptions.RequestException as e:
        return f"Error accessing website: {e}"
    except Exception as e:
        return f"Error processing website: {e}"

def summarize_text(text, summary_type):
    try:
        if len(text) > 10000:
            text = text[:10000] + "..."
        prompts = {
            "1": f"Please summarize this website content in a general overview, about 300-400 words and include the main points:\n\n{text}",
            "2": f"Summarize the following content as an article summary:\n\nInclude a title, introduction, main points, supporting details, and a conclusion. Focus on clarity and conciseness:\n\n{text}",
            "3": f"Summarize the following content as a project summary:\n\nInclude the purpose, steps taken, results, and implications:\n\n{text}",
            "4": f"Summarize the following content in bullet points, highlighting key takeaways:\n\n{text}",
            "5": f"Summarize the following content as a research summary:\n\nInclude the research question, methodology, results, and conclusion:\n\n{text}",
            "6": f"Summarize the following content as a resume summary:\n\nHighlight relevant skills and experience, and present as a brief professional profile:\n\n{text}"
        }
        prompt = prompts.get(summary_type, prompts["1"])
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error creating summary: {e}"

def create_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)
    pdf.output(filename)
    return filename

def create_docx(text, filename):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)
    return filename

st.title("AI Website Summarizer")

url = st.text_input("Enter website URL:")
if not url:
    st.warning("Please enter a valid URL")
    st.stop()

if not url.startswith(('http://', 'https://')):
    url = 'https://' + url

with st.spinner("Getting website content..."):
    website_text = get_website_text(url)
    if website_text.startswith("Error"):
        st.error(website_text)
        st.stop()

summary_type = st.selectbox(
    "Choose summary type:",
    [
        "Default summary (general overview)",
        "Article summary",
        "Project summary",
        "Bullet summary",
        "Research summary",
        "Resume summary"
    ]
)
summary_type_key = str(summary_type.index(summary_type) + 1)

with st.spinner("Creating summary..."):
    summary = summarize_text(website_text, summary_type_key)

st.subheader("Summary")
st.markdown("---")
st.write(summary)
st.markdown("---")

save_option = st.radio(
    "Do you want to save the summary?",
    ["No", "PDF", "DOCX"]
)

if save_option != "No":
    filename = st.text_input("Enter the filename (without extension):", value="website_summary")
    if st.button("Save"):
        if save_option == "PDF":
            file_path = create_pdf(summary, f"{filename}.pdf")
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download PDF",
                    data=f,
                    file_name=f"{filename}.pdf",
                    mime="application/pdf"
                )
        else:
            file_path = create_docx(summary, f"{filename}.docx")
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download DOCX",
                    data=f,
                    file_name=f"{filename}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
