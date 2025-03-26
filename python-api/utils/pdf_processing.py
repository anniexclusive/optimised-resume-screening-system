import PyPDF2

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF resume (given a PDF file object) and cleans it."""
    if isinstance(pdf_file, str):  # If the input is a file path, open the file
        with open(pdf_file, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            text = text.lower()  # Convert to lowercase
    else:  # If the input is already a file object
        reader = PyPDF2.PdfReader(pdf_file)
        text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        text = text.lower()  # Convert to lowercase
    return text 