# BriefBot

BriefBot is a Streamlit app that fetches website content and generates AI summaries with Google Gemini. You can choose a summary style and export results as PDF or DOCX.

## Features

- Extracts readable text from a webpage using BeautifulSoup
- Generates AI summaries with multiple formats
- Supports download as PDF or DOCX
- Simple Streamlit UI for quick use

## Prerequisites

- Python 3.9+
- A Google Gemini API key

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd BreifBot
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

## Run the app

```bash
streamlit run main.py
```

Open the local URL shown by Streamlit (usually `http://localhost:8501`).

## How to use

1. Enter a website URL.
2. Choose a summary type:
   - Default summary (general overview)
   - Article summary
   - Project summary
   - Bullet summary
   - Research summary
   - Resume summary
3. Wait for the generated summary.
4. Optionally export as PDF or DOCX.

## Project structure

```text
BreifBot/
├── main.py
├── requirements.txt
├── readme.md
└── website_summary.pdf
```

## Troubleshooting

- **`Error accessing website`**: verify the URL is public and reachable.
- **Gemini/API errors**: confirm `GEMINI_API_KEY` is set correctly in `.env`.
- **Dependency issues**: update pip and reinstall:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Notes

- Some websites block scraping or require JavaScript rendering.
- Output quality depends on source content quality and model behavior.
