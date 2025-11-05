"""
PDF Processing utilities
Uses pypdf (maintained fork of PyPDF2)
"""
from pypdf import PdfReader


def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF resume.

    Args:
        pdf_file: File path (str) or file object

    Returns:
        str: Extracted text in lowercase

    SRE Note: pypdf is the maintained fork of PyPDF2
    """
    try:
        if isinstance(pdf_file, str):  # If the input is a file path, open the file
            with open(pdf_file, "rb") as file:
                reader = PdfReader(file)
                text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
                text = text.lower()  # Convert to lowercase
        else:  # If the input is already a file object
            reader = PdfReader(pdf_file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            text = text.lower()  # Convert to lowercase
        return text
    except Exception as e:
        # Log error and re-raise for upstream handling
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
