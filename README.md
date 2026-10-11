# Ask VMM

Ask VMM is a lightweight Dutch/English question-answering prototype for public VMM environmental reports. It downloads a small set of official PDFs, extracts their text, indexes the content, and answers user questions by ranking the most relevant passages. When the evidence is too weak, it responds with “Ik weet het niet” instead of inventing an answer.

## What it does

- Loads a small corpus of public VMM reports in the data folder
- Extracts text from PDF pages with PyPDF
- Builds a TF-IDF retrieval index over the extracted content
- Returns a concise answer together with document/page citations
- Refuses unsupported questions when relevance is too low

## Included sources

The app is built around these public VMM documents:

- Gemeenschappelijke Maas waterkwaliteit
- Luchtkwaliteitsmeetcampagne 2021
- Educatief pakket luchtkwaliteit
- BelAQI persbericht
- Luchtbeleidsplan bijlage 4

## Local setup

1. Create a virtual environment:
   python -m venv .venv
2. Activate it:
   - Windows PowerShell: .\.venv\Scripts\Activate.ps1
   - Windows Command Prompt: .\.venv\Scripts\activate.bat
3. Install dependencies:
   python -m pip install -r requirements.txt
4. Start the app:
   streamlit run app.py

## Optional environment configuration

Copy the example file if needed:

- .env.example to .env

The default data folder is data/reports.

## Evaluation

The project includes a lightweight validation script:

- python scripts/evaluate.py

This checks 10 representative questions against the real document corpus and prints a pass/fail summary. A fresh local run is the recommended proof step before demoing the prototype.

## Demo flow

1. Open the app in a browser.
2. Enter a VMM question in Dutch or English.
3. Read the answer and source references.
4. Test a borderline question to confirm that the app answers carefully and declines unsupported requests.

## Notes

- The prototype is intentionally local and document-scoped.
- It is designed for a judged demo rather than a production-grade search system.
- It relies on official public PDF sources and not on external API calls.
