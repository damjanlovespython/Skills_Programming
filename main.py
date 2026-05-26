"""
=== CV Job Matcher ===
Main script that orchestrates the full pipeline:
1. User selects their CV and provides the job offer (URL, paste, or file)
2. Text is extracted from both
3. Keywords are parsed and structured
4. A matching score is computed
5. Results are displayed to the user
"""

import sys
from tkinter import Tk, filedialog
from CV_Upload import extract_text, extract_from_url, clean_text

# ============================================================
# Module imports (uncomment as you build each module)
# ============================================================
# from parser import parse_cv, parse_job
# from scorer import compute_score


# ============================================================
# File Selection
# ============================================================

def select_file(prompt):
    """
    Opens a file dialog window so the user can browse and select a file.
    """
    while True:                                                                                                                 # create an infinite loop in order for the program to ask again
        print(prompt)
        root = Tk()                                                                                                             # create the Tkinker application window (basic graphical interface)
        root.withdraw()                                                                                                         # hide empty window
                                                                                                                                # open the selected window and only show the file that we can handle (pdf,txt,docx)
        filepath = filedialog.askopenfilename(title=prompt, filetypes=[("All supported", "*.pdf *.docx *.txt"), ("PDF files", "*.pdf"), ("Word documents", "*.docx"), ("Text files", "*.txt")])
        root.destroy()                                                                                                              # destroy the window once it has been created
                                                                                                                                # handle the case where no file was selected (error so return None)
        if filepath:    
            return filepath                                                                                                     # general case return the file path
        
        retry = input("No file selected. Try again? (YES/NO): ").strip().lower()                                                # adds a loop for the user to have another chance
        if retry != "yes":
            return None


# ============================================================
# Job Offer Input: cascading approach (URL → paste → file)
# ============================================================

def get_job_text():
    """
    Gets the job offer text using a cascading approach:
    1. First try: user provides a URL and we fetch the page
    2. If that fails: user can paste the text directly
    3. Last resort: user uploads a file
    Returns: The cleaned job offer text
    """
    while True:
        # Try 1: URL
        print("\n--- Job Offer Input ---")                                                                                      # nice formating of the output
        url = input("Paste the URL of the job offer (or press Enter to skip): ").strip()                                        # input from the user (URL)

        if url: 
            print("Fetching job offer from URL...")                                                                             # extracting job information
            job_text = extract_from_url(url)                                                        

            if job_text:
                print(f"  Success! Extracted {len(job_text)} characters from URL.")                                             # simply check the lenght of the document
                return job_text
            else:
                print("  Could not extract text from this URL. Let's try another method.\n")                                    # handle error

        # Try 2: Copy-paste 
        print("Would you like to paste the job description directly?")
        choice = input("Type YES to paste, or NO to upload a file instead: ").strip().lower()                                   # input from the user (choice)

        if choice == "yes":
            print("\nPaste the job description below.")                                                                         # nice formating
            print("When you're done, type END on a new line and press Enter.")                                                  # concrete input (job description). note that we need the end otherwise the loop keep going forward and the program crashes
            print("-" * 30)                                                                                             

            lines = []                                                                                                          # storage of the content
            while True:                                                                                                         # use an infinite loop to clean the job description from the user ()
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)

            raw_text = "\n".join(lines)                                                                                         # use the lines and put them all in one unique line (stead of the list of components)
            job_text = clean_text(raw_text)                                                                                     # apply the cleaning function on the input

            if job_text:
                print(f"\n  Success! Captured {len(job_text)} characters.")                                                     # check to see if it works (None if it does not)
                return job_text
            else:
                print("  No text was captured. Let's try uploading a file.\n")

        # Try 3: File upload -> last try 
        print("Please select the job offer file...")
        job_path = select_file("Select the job offer file...")                                                                  # same system as for the CV (upload a copy of the job description)

        if  job_path:                                                                                                        
            job_text = extract_text(job_path)                                                                                                           
            print(f"  Success! Extracted {len(job_text)} characters from file.")
            return job_text
        
        # Everything failed - ask before looping back
        retry = input("\nCould not get job offer text. Try again? (yes/no): ").strip().lower()                                 # ask the user if want to try again
        if retry != "yes":
            print("Thank you for using CV Job Matcher. Goodbye!")                                                              # if refuse put end to the loop and quite program
            sys.exit(0)


# ============================================================
# Main Program
# ============================================================

def main():
    print("=" * 50)
    print("         CV JOB MATCHER")
    print("=" * 50)

    # --- Step 1: Get the CV ---
    print("\nStep 1: Select your CV")
    print("-" * 30)
    cv_path = select_file("Select your CV...")
    if not cv_path:
        print("Thank you for using CV Job Matcher. Goodbye!")
        return
    cv_text = extract_text(cv_path)
    print(f"  CV loaded: {len(cv_text)} characters extracted")

    # --- Step 2: Get the job offer (URL -> paste -> file) ---
    print("\nStep 2: Provide the job offer")
    print("-" * 30)
    job_text = get_job_text()

    # --- Step 3: Parse and extract keywords ---
    print("\nStep 3: Analyzing documents...")
    print("-" * 30)
    # TODO: uncomment when parser.py is ready
    # cv_data = parse_cv(cv_text)
    # job_data = parse_job(job_text)
    print("  [Parser module not yet built]")
    print(f"  CV preview: {cv_text[:100]}...")
    print(f"  Job preview: {job_text[:100]}...")

    # --- Step 4: Compute matching score ---
    print("\nStep 4: Computing match score...")
    print("-" * 30)
    # TODO: uncomment when scorer.py is ready
    # result = compute_score(cv_data, job_data)
    print("  [Scorer module not yet built]")

    # --- Step 5: Display results ---
    print("\nStep 5: Results")
    print("-" * 30)
    # TODO: replace with actual results
    print("  [Results will appear here once all modules are complete]")

    print("\n" + "=" * 50)
    print("  Thank you for using CV Job Matcher!")
    print("=" * 50)


if __name__ == "__main__":
    main()
