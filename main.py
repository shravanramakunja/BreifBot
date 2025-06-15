import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF
from docx import Document
import streamlit as st


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
     "1": f"Write a conversational, general overview of the website content as a single paragraph (about 5000–4000 words). Focus on summarizing the main themes and purpose in a way that is easy for anyone to understand. Do not use bullet points or numbered lists.\n\n{text}",
    "2": f"Summarize this content as a formal article. Start with a concise, informative title. Then, provide a brief introduction, followed by main points with supporting details, and conclude with a final thought. Use clear section headings for each part. Keep the tone formal and avoid bullet points.\n\n{text}",
    "3": f"Summarize this content as a structured project summary. Begin with the project's purpose or objective. Then, outline the main steps or stages. Next, describe the results or outcomes, and finish by discussing the implications or impact. Use labeled sections for each part. Keep the tone professional and factual.\n\n{text}",
    "4": f"Summarize the main content as a numbered list. Each numbered point should be a short, clear statement capturing a key idea, feature, or insight about the website. Use your own words. Prioritize the most important and unique information. Limit the summary to 5–10 numbered bullets. Do not use paragraphs or section headings.\n\nExample format:\n1. About the website\n2. Description of the website\n3. Main features or purpose\n4. Unique insights or key information\n5. Important highlights\n\n{text}",
    "5": f"Summarize this content as an IEEE research paper abstract. Structure your summary as follows: Start with the word 'Abstract' (italicized and bold), followed by an em dash. Then, provide a concise, self-contained summary of the research question, methodology, main findings, and conclusions. Keep the abstract to one paragraph, 150–250 words. End with a list of keywords relevant to the content. Use a formal, academic tone. Example:\n\n*Abstract* **—This study investigates ... The methodology ... The results show ... The conclusion ...**\n\nKeywords: keyword1, keyword2, keyword3\n\n{text}",
    "6": f"Summarize this content as a professional resume summary. Highlight the most relevant skills, experience, and achievements. Present the information as a brief, polished professional profile suitable for a resume. Keep it concise and focused on qualifications and suitability for a job. Use a professional tone and avoid bullet points.\n\n{text}"
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

st.title("BriefBot")
st.write("Summarize any website content with ease using AI ")
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
