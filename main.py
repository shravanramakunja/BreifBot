import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF
from docx import Document
# Load environment variables
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def get_website_text(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
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
        
        # Define prompts for each summary type
        prompts = {
            "1": f"Please summarize this website content in a general overview, about 300-400 words and include the main points:\n\n{text}",
            "2": f"Summarize the following content as an article summary:\n\nInclude a title, introduction, main points, supporting details, and a conclusion. Focus on clarity and conciseness:\n\n{text}",
            "3": f"Summarize the following content as a project summary:\n\nInclude the purpose, steps taken, results, and implications:\n\n{text}",
            "4": f"Summarize the following content in bullet points, highlighting key takeaways:\n\n{text}",
            "5": f"Summarize the following content as a research summary:\n\nInclude the research question, methodology, results, and conclusion:\n\n{text}",
            "6": f"Summarize the following content as a resume summary:\n\nHighlight relevant skills and experience, and present as a brief professional profile:\n\n{text}"
        }
        prompt = prompts.get(summary_type, prompts["1"])  # Default to general if not found
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error creating summary: {e}"

def save_as_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)
    pdf.output(filename)
    print(f"Summary saved as PDF: {filename}")

def save_as_docx(text, filename):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)
    print(f"Summary saved as DOCX: {filename}")

def main():
    print("=== AI Website Summarizer ===")
    print()
    url = input("Enter website URL: ").strip()
    if not url:
        print("Please enter a valid URL")
        return
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    print("Getting website content...")
    website_text = get_website_text(url)
    if website_text.startswith("Error"):
        print(website_text)
        return

    # Prompt for summary type
    print("\nChoose summary type:")
    print("1. Default summary (general overview)")
    print("2. Article summary")
    print("3. Project summary")
    print("4. Bullet summary")
    print("5. Research summary")
    print("6. Resume summary")
    while True:
        summary_type = input("Enter choice (1-6): ").strip()
        if summary_type in ["1", "2", "3", "4", "5", "6"]:
            break
        print("Invalid choice. Please enter a number from 1 to 6.")

    print("Creating summary...")
    summary = summarize_text(website_text, summary_type)
    print("\n" + "="*50)
    print("SUMMARY:")
    print("="*50)
    print(summary)
    print("\n" + "="*50)

    # Ask user if they want to save the summary
    while True:
        choice = input("Do you want to save the summary as (P)DF, (D)OCX, or (N)othing? [P/D/N]: ").strip().upper()
        if choice in ['P', 'D', 'N']:
            break
        print("Invalid choice. Please enter 'P' for PDF, 'D' for DOCX, or 'N' for nothing.")

    if choice == 'N':
        print("Summary not saved. Exiting.")
        return

    filename = input("Enter the filename (without extension): ").strip()
    if not filename:
        filename = "website_summary"

    if choice == 'P':
        save_as_pdf(summary, f"{filename}.pdf")
    else:
        save_as_docx(summary, f"{filename}.docx")

if __name__ == "__main__":
    main()
