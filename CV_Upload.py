"""
Module for CV : 

File Handling and Text Extraction: 
This module handles reading files in different formats (PDF, DOCX, TXT)
and extracting clean text from them.
"""

# library
import docx
import requests
# function import
from pypdf import PdfReader
from pathlib import Path
from bs4 import BeautifulSoup

# function definition:

# need to define the file we can handle: 
# most common use are PDF, txt and docx
def extract_text(filepath):
    """
    Input: This function takes the path of the document (CV) that the user want to upload.
    Aims: Extract text from a .txt, .pdf, or .docx file. Those are the main one and is thus flexible for the user usage
    The function automatically detects the file type using the file extension.
    Supported formats: .txt / .pdf / .docx
    """
    # conditional structure use to identify the file that the user just uploaded
    filepath = Path(filepath)                                           # concerte the path into an object path and not simply a string
    # Check if the file actually exists before trying to read it
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    extension = filepath.suffix.lower()                                 # isolate the suffix of the file (type (.txt)) and transform it into lowercase to be able to sort the different file according to their type                
    # handle txt file
    if extension == ".txt":
        with open(filepath, "r", encoding="utf-8") as file:             # open the file as read and interpret it using UTF-8
            raw_text = file.read()
    # handle pdf file
    elif extension == ".pdf":
        reader = PdfReader(filepath)                                    # create a pdf object
        text = ""                                                       # string is empty but text is going to be stored here
        for page in reader.pages:                                       # loops through every page of the document                                  # 
            page_text = page.extract_text()                             # extract text
            if page_text:
                text += page_text + "\n"                                # check the extracted text (return None if empty) and create a new line for each new page of file
        raw_text = text
    # handle the docx file
    elif extension == ".docx":
        doc = docx.Document(filepath)                                   # create a docx object
        text = ""                                                       # same mechanism as the pdf
        for paragraph in doc.paragraphs:                                # add a new line for each paragraphs
            text += paragraph.text + "\n"
        raw_text = text
    # handle the possible error linked to another type of file being added
    else:
        raise ValueError(f"Unsupported file format: {extension}")
    # Clean the text and check if anything was extracted
    cleaned = clean_text(raw_text)
    # handle error
    if not cleaned:
        print(f"Warning: No text could be extracted from {filepath}")
    # return the result
    return cleaned

# extraction of job-offer (URL version)
def extract_from_url(url):
    """
    Extract text content from a webpage URL.
    Uses requests to fetch the page and BeautifulSoup to parse the HTML.
    Parameters: URL of the job offer page
    Returns: The cleaned text content of the page, or None if extraction failed
    """
    try:# safety net when we try to download the webpage                                                                
        # Fetch the webpage
        # some sites block requests without a user agent 
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}                        
        response = requests.get(url, headers=headers, timeout=10)       # timeout after 10 seconds if site doesn't respond
        response.raise_for_status()                                     # raise an error if the request failed (e.g. 404) otherwise it means it return nothing 

        # Parse the HTML content (webpage are build on html content)
        soup = BeautifulSoup(response.text, "html.parser")              # beautifulSoup turns that HTML into an object python can handle

        # Remove script and style elements (not useful text) from the html handout given by BeautfifulSoup
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()                                         # completely removes these elements from the page

        # Extract the visible text
        raw_text = soup.get_text(separator="\n")                        # get all remaining text, separated by newlines

        cleaned = clean_text(raw_text)                                  # finally apply the function of cleaning 

        if not cleaned:                                                 # error message 
            print("Warning: No text could be extracted from the URL.")
            return None

        return cleaned                                                  # return clean

    # handling the different issue linked with the download of the page
    except requests.exceptions.Timeout:
        print("Error: The website took too long to respond.")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the website. Check the URL.")
        return None
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None






# analysis of the text

def clean_text(text):
    """
    Clean the extracted text by:
    - Removing extra whitespace and blank lines
    - Stripping leading/trailing spaces
    - Replacing multiple spaces with single spaces
    This ensures consistent text regardless of the source format.
    """
    # Fix PDF artifacts before anything else
    text = text.replace("-\n", "")                                      # rejoin words broken across lines (e.g. "manage-\nment" -> "management")
    text = text.replace("\u2019", "'")                                  # smart quote to normal quote (strange printing issue for every pdf document)
    text = text.replace("\u2018", "'")                                  # smart quote to normal quote
    text = text.replace("\u2013", "-")                                  # en dash to hyphen (same issue when printing pdf return error due to specific character that python cannot handle)
    text = text.replace("\u2014", "-")                                  # em dash to hyphen
    text = text.replace("\u2022", " ")                                  # bullet point to space (bullet point aren't recognize and they are present in most of the CV so we needed to change those)
    text = text.replace("\xa0", " ")                                    # non-breaking space to normal space (still issue of character difference between Python and .pdf)
    # Split into lines, strip each one, remove empty lines
    lines = text.split("\n")                                            # split at each new line
    cleaned_lines = []                                                  # future storage of the clean text
    for line in lines:                                                  # loop through each line
        stripped = line.strip()                                         # remove the space (at the begining and the end of each string)
        if stripped:                                                    # skip empty lines
            cleaned = " ".join(stripped.split())                        # replace multiple spaces with a single space
            cleaned_lines.append(cleaned)
    return "\n".join(cleaned_lines)                                     # return the new clean text with new lines already in text













# ============================================================
# This section runs only when you execute this file directly
# (not when you import it from another module)
# It's useful for testing the module on its own.
# ============================================================
if __name__ == "__main__":
    import sys

    # You can test by running: python CV_Upload.py my_file.pdf
    if len(sys.argv) < 2:
        print("Usage: python extractor.py <filepath>")
        print("Example: python extractor.py resume.pdf")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        text = extract_text(filepath)
        print(f"Successfully extracted text from: {filepath}")
        print(f"Character count: {len(text)}")
        print(f"Line count: {len(text.split(chr(10)))}")
        print("-" * 50)
        print(text)
    except Exception as e:
        print(f"Error: {e}")