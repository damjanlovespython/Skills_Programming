# CV Job Matcher: Match your CV against any job offer in seconds.
## Short description
CV Job Matcher is a web-based tool that compares a candidate's CV against a job offer and returns a structured match score. It extracts keywords from both documents, groups synonyms, and breaks down the result by category so the user knows exactly what is missing and what is already covered.
## Features
- Upload a CV in PDF, DOCX, or TXT format
- Provide a job offer via URL, copy-paste, or file upload
- Automatic text extraction and cleaning for all supported file types
- Keyword extraction across six categories: technical skills, programming languages, soft skills, contextual skills, finance skills, and spoken languages
- Synonym resolution (e.g. "JS" and "JavaScript" count as the same skill)
- Weighted match score from 0 to 100 with a bonus for required skills
- Per-category breakdown with matched and missing skill lists
- Skill importance tags extracted from the job offer (required / preferred / responsibility)
- Experience requirement detection (e.g. "3+ years of experience in Python")
- Browser-based interface built with Streamlit (no terminal required)
## Technologies used
- **Python 3.14**
- **Streamlit**; web interface
- **pypdf**; PDF text extraction
- **python-docx**; DOCX text extraction
- **BeautifulSoup4**; HTML parsing for URL-based job offers
- **Selenium + Chromium**; fallback browser for JavaScript-heavy job pages
- **requests**; HTTP fetching
- **pathlib**; file path handling
- **re**; regular expression keyword matching
## Installation
### Prerequisites
Make sure Python 3.14 or higher is installed. You can download it from https://www.python.org/downloads/.
To verify your Python version, open a terminal and run:
```bash
python --version
```
### Windows
1. Download or clone the repository and open the project folder in VS Code (right-click the folder and select "Open with Code").
2. Open the terminal in VS Code: Terminal → New Terminal.
3. Install uv:
```bash
   pip install uv
```
4. Install all dependencies:
```bash
   uv sync
```
5. Run the app:
```bash
   uv run streamlit run app.py
```
Note: The Selenium fallback for JavaScript-heavy job pages is not supported natively on Windows without WSL. The simple URL extraction via requests will still work for most job postings.
### macOS
1. Download or clone the repository and open the project folder in VS Code (right-click the folder and select "Open with Code").
2. Open the terminal in VS Code: Terminal → New Terminal.
3. Install uv:
```bash
   pip install uv
```
4. Install all dependencies:
```bash
   uv sync
```
5. Install Chromium for the Selenium fallback (requires Homebrew):
```bash
   brew install chromium chromedriver
```
6. Run the app:
```bash
   uv run streamlit run app.py
```
### Linux
1. Download or clone the repository and open the project folder in VS Code (right-click the folder and select "Open with Code").
2. Open the terminal in VS Code: Terminal → New Terminal.
3. Install system packages required for the Selenium fallback:
```bash
   sudo apt update && sudo apt install -y chromium chromium-driver
```
4. Install uv:
```bash
   pip install uv
```
5. Install all dependencies:
```bash
   uv sync
```
6. Run the app:
```bash
   uv run streamlit run app.py
```
The app will open at `http://localhost:8501` on all operating systems.
### Windows
1. Download or clone the repository and open the project folder in VS Code (right-click the folder and select "Open with Code").
2. Open the terminal in VS Code: Terminal → New Terminal.
3. Install uv:
## Usage
1. **Upload your CV**: Drag and drop or browse for your CV file (PDF, DOCX, or TXT).
2. **Provide the job offer**: Paste the URL of the job posting, type or paste the job description directly, or upload a file.
3. Click **Analyse Match**.
4. **Results**: View your overall score, per-category percentages, and a full matched/missing breakdown across six tabs.
## Structure

```
.
├── app.py                  # Streamlit web interface (main entry point)
├── main.py                 # Terminal-based interface (alternative entry point)
├── CV_Upload.py            # File reading and text extraction
├── Structure_Parser.py     # Keyword extraction and document parsing
├── scorer.py               # Match scoring logic
├── playground.py           # Development scratch file
├── pyproject.toml          # Project metadata and dependencies
├── packages.txt            # System packages (chromium, chromium-driver)
├── devcontainer.json       # GitHub Codespaces / VS Code dev container config
└── README.md               # Documentation
```

## Modules
### `CV_Upload.py`
Handles file reading and text extraction. Supports PDF (via pypdf), DOCX (via python-docx), and TXT. Also fetches job offer text from URLs using requests + BeautifulSoup, with a Selenium fallback for JavaScript-rendered pages. Includes a `clean_text()` function that normalises encoding artefacts (smart quotes, em dashes, bullet points, non-breaking spaces) and removes blank lines.

### `Structure_Parser.py`
Parses the cleaned text and extracts structured keyword data. Contains large keyword lists for programming languages, CS skills, finance, mathematics, physics, medicine, law, marketing, consulting, soft skills, education levels, and spoken languages. Key functions:
- `parse_cv(text)` — extracts what the candidate has
- `parse_job(text)` — extracts what the job requires, including importance tags and experience requirements
- `resolve_synonyms(keywords)` — groups variant spellings under a canonical name
- `extract_language_proficiency(text)` — detects language and proficiency level
- `find_contextual_skills(text)` — detects soft skills described in sentences rather than listed as keywords
- `tag_keyword_importance(keyword, sections)` — classifies each keyword as required, preferred, or responsibility

### `scorer.py`
Takes the two parsed dictionaries and computes a match score. Uses a weighted average across six categories (technical 35%, programming 20%, soft 15%, contextual 10%, finance 10%, languages 10%) plus a bonus of up to 10 points for covering required skills. Returns a full breakdown dict with matched and missing lists for each category. Includes defensive input validation that returns a zero score with an error message rather than crashing when the parser output is malformed.

### `app.py`
Streamlit web interface. Manages session state so results persist after the button press triggers a script rerun. Renders the hero banner, upload widgets, score box, per-category metric cards, six skill breakdown tabs, importance tag expander, experience requirements expander, and a reset button.

### `main.py`
Terminal-based alternative to `app.py`. Uses Tkinter file dialogs for CV selection and cascading input methods (URL → paste → file) for the job offer. Useful for testing the pipeline without running Streamlit.
## How it works
1. The user uploads a CV and provides a job offer.
2. `CV_Upload.py` extracts and cleans the raw text from both.
3. `Structure_Parser.py` scans both texts against keyword lists, resolves synonyms, and tags job keywords by importance.
4. `scorer.py` computes the overlap between the two parsed documents in each category, combines the ratios with fixed weights, adds a required-skills bonus, and returns a final integer score from 0 to 100.
5. `app.py` renders the results as a score box, metric cards, and tabbed skill breakdowns.
## Prupose of the project
This project was built as part of the Skills Programming course. The goal was to apply Python programming concepts to a practical problem: helping job applicants understand how well their CV matches a given job description, and identifying which skills to highlight or add.
## Authors
Abisanth ..., Damjan ..., Manuel Altmann, Pamir ... and William ...
## Further Questions
For questions about the codebase contact the project authors directly.
