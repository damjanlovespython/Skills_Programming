"""
Module for CV : 

File Handling and Text Extraction: 
This module handles reading files in different formats (PDF, DOCX, TXT)
and extracting clean text from them.
"""

# library
import os
import docx

# function import
from pypdf import PdfReader
from pathlib import Path

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
    filepath = Path(filepath)
    extension = filepath.suffix.lower()
    # handle txt file
    if extension == ".txt":
        return extract_from_txt(filepath)
    # handle pdf file
    elif extension == ".pdf":
        return extract_from_pdf(filepath)
    # handle the docx file
    elif extension == ".docx":
        return extract_from_docx(filepath)
    # handle the possible error linked to another type of file being added
    else:
        raise ValueError(f"Unsupported file format: {extension}")

# define the function called before in order to handle all file as one, once they are added to the docuement.
# handle all the file in the dcouemnt
def extract_from_txt(filepath):
    """
    Extract text from a plain text file.
    """
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()

def extract_from_pdf(filepath):
    """
    Extract text from a PDF file using pypdf.
    """
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"
    return text


def extract_from_docx(filepath):
    """
    Extract text from a Word .docx file using python-docx.
    """
    doc = docx.Document(filepath)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text





# analysis of the text

def clean_text(text):
    """
    Clean the extracted text by:
    - Removing extra whitespace and blank lines
    - Stripping leading/trailing spaces
    - Replacing multiple spaces with single spaces

    This ensures consistent text regardless of the source format.
    """
    # Split into lines, strip each one, remove empty lines
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped:  # skip empty lines
            # Replace multiple spaces with a single space
            cleaned = " ".join(stripped.split())
            cleaned_lines.append(cleaned)

    return "\n".join(cleaned_lines)


def extract_text(filepath):
    """
    Main function: extracts and cleans text from any supported file type.

    How it works:
    1. Checks if the file exists
    2. Detects the file type from the extension
    3. Calls the appropriate extraction function
    4. Cleans the result before returning

    Supported formats: .pdf, .docx, .txt

    Parameters:
        filepath (str): Path to the file to extract text from

    Returns:
        str: The cleaned text content of the file

    Example:
        >>> text = extract_text("resume.pdf")
        >>> print(text[:100])  # print first 100 characters
    """
    # Step 1: Check if file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Step 2: Get the file extension (lowercase for consistency)
    _, extension = os.path.splitext(filepath)
    extension = extension.lower()

    # Step 3: Call the right extraction function based on file type
    if extension == ".pdf":
        raw_text = extract_from_pdf(filepath)
    elif extension == ".docx":
        raw_text = extract_from_docx(filepath)
    elif extension == ".txt":
        raw_text = extract_from_txt(filepath)
    else:
        raise ValueError(
            f"Unsupported file format: '{extension}'\n"
            f"Supported formats: .pdf, .docx, .txt"
        )

    # Step 4: Clean and return
    cleaned = clean_text(raw_text)

    if not cleaned:
        print(f"Warning: No text could be extracted from {filepath}")

    return cleaned


# ============================================================
# This section runs only when you execute this file directly
# (not when you import it from another module)
# It's useful for testing the module on its own.
# ============================================================
if __name__ == "__main__":
    import sys

    # You can test by running: python extractor.py my_file.pdf
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