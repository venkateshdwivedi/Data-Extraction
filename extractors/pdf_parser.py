import pdfplumber

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text from a given PDF file.
    
    Args:
        pdf_path (str): The path to the PDF file.
        
    Returns:
        str: The complete extracted text from all pages.
    """
    full_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text from the page; extract_text() returns None if no text found
            text = page.extract_text()
            if text:
                full_text.append(text)
                
    # Join all pages with a newline separator
    return "\n".join(full_text)
