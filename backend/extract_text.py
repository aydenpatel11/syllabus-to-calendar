from pathlib import Path
from typing import Optional
import pdfplumber

def extract_from_pdf(pdf_path: Path) -> str:
    """
    Extract raw text from a syllabus PDF.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        str: Extracted text
    """
    if pdf_path.exists():
        with pdfplumber.open(pdf_path) as pdf:
            text_parts = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:  
                    text_parts.append(page_text)
            return "\n\n".join(text_parts)  
    else:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

def extract_from_text_file(text_file_path: Path) -> str:
    """
    Extract raw text from a text file.

    Args:
        text_file_path (str): Path to the text file
    """
    if text_file_path.exists():
        with open(text_file_path, "r", encoding="utf-8") as file:
            return file.read()
    else:
        raise FileNotFoundError(f"Text file not found: {text_file_path}")


def extract_text(file_path: Path) -> str:
    """
    Extract raw text from a file.

    Args:
        file_path (str): Path to the file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_path.suffix.lower() == ".pdf":
        return extract_from_pdf(file_path)
    elif file_path.suffix.lower() == ".txt":
        return extract_from_text_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

## testing the functions
if __name__ == "__main__":
    # Test text file extraction (doesn't require pdfplumber)
    print("Testing text file extraction...")
    text_path = Path("sample_syllabi/test_syllabus.txt")
    if text_path.exists():
        text = extract_from_text_file(text_path)
        print("Text file extraction successful!")
        print(f"Extracted {len(text)} characters")
        print("\nFirst 200 characters:")
        print(text[:200])
    else:
        print(f"Test file not found: {text_path}")
    
    print("\n" + "="*50 + "\n")
    
    # Test PDF extraction (requires pdfplumber)
    print("Testing PDF extraction...")
    pdf_path = Path("sample_syllabi/sample_syllabus.pdf")
    if pdf_path.exists():
        try:
            text = extract_from_pdf(pdf_path)
            print("PDF extraction successful!")
            print(f"Extracted {len(text)} characters")
            print("\nFirst 200 characters:")
            print(text[:200])
        except Exception as e:
            print(f"Error extracting PDF: {e}")
    else:
        print(f"PDF file not found: {pdf_path}")
    
    print("\n" + "="*50 + "\n")
    
    # Test main extract_text function
    print("Testing extract_text() routing...")
    if text_path.exists():
        text = extract_text(text_path)
        print(f"extract_text() successfully routed to text extraction: {len(text)} characters")