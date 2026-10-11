# Ask VMM

Ask VMM is a lightweight question-answering prototype for public VMM environmental reports. It downloads a small set of official PDFs into `data/reports`, extracts their text, and answers questions by ranking the most relevant passages. When the evidence is too weak, it responds with "Ik weet het niet" instead of inventing an answer.

## What it does

- Downloads a small corpus of public VMM reports into `data/reports` when they are not already present
- Extracts text from PDF pages with PyPDF
- Combines word-level and character-level TF-IDF retrieval to handle normal wording, compounds, and inflections
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

This checks representative answerable, English, and deliberately unsupported questions against the real document corpus. It reports:

- strict pass/fail: answer content and expected source must both match for answerable questions
- hit@3: whether the expected document appears in the top three citations
- refusal accuracy: whether unsupported questions return no answer and no sources

The project also has focused tests:

- python -m pytest -q

GitHub Actions runs the same tests on pushes and pull requests.

## Architecture

```text
VMM PDF URLs
   -> download/cache in data/reports
   -> page-level text extraction
   -> word TF-IDF + character TF-IDF indexes
   -> weighted cosine ranking
   -> best sentence + top-three document/page citations
   -> refusal when relevance or question/answer overlap is too weak
```

This is retrieval plus extractive answering, rather than an LLM-generated RAG answer. That is deliberate: the baseline is local, measurable, cheap to run, and easier to audit.

## Demo flow

1. Open the app in a browser.
2. Enter a VMM question in Dutch or English.
3. Read the answer and source references.
4. Test a borderline question to confirm that the app answers carefully and declines unsupported requests.

## Notes

- The prototype is intentionally local and document-scoped.
- It relies on official public PDF sources and not on external API calls.
- English retrieval is limited when an English question uses terminology that does not overlap with the Dutch source text. A multilingual embedding retriever would be the next retrieval experiment.
- PDF table extraction and scanned PDFs are not handled reliably; numeric answers need table-aware extraction and extra verification.
- The refusal threshold is a conservative baseline and should be calibrated on a separate validation set before production use.

## Production direction

For a real VMM deployment, the next version would add multilingual embeddings or a hybrid BM25/embedding retriever, a strictly grounded answer-generation step with passage-level citations, document refresh and versioning, authentication and role-based access, telemetry for refusals and failed retrievals, and an evaluation set maintained separately from tuning data.
