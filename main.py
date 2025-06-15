import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF
from docx import Document

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

def summarize_text(text):
    try:
        if len(text) > 10000:
            text = text[:10000] + "..."
        prompt = f"Please summarize this website content in terms like about 3000-4000 words and the main bullet points of the website:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error creating summary: {e}"

def save_as_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Split text into chunks to fit page width
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

    print("Creating summary...")
    summary = summarize_text(website_text)
    print("\n" + "="*50)
    print("SUMMARY:")
    print("="*50)
    print(summary)
    print("\n" + "="*50)

    # Ask user for output format
    while True:
        choice = input("Do you want to save the summary as (P)DF or (D)OCX? [P/D]: ").strip().upper()
        if choice in ['P', 'D']:
            break
        print("Invalid choice. Please enter 'P' for PDF or 'D' for DOCX.")

    filename = input("Enter the filename (without extension): ").strip()
    if not filename:
        filename = "website_summary"

    if choice == 'P':
        save_as_pdf(summary, f"{filename}.pdf")
    else:
        save_as_docx(summary, f"{filename}.docx")

if __name__ == "__main__":
    main()
