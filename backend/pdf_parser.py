import pdfplumber
import io
import re


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract and clean text from a PDF file provided as bytes."""
    try:
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        full_text = "\n".join(text_parts)
        if not full_text.strip():
            raise ValueError("Could not extract text from PDF")
        return clean_text(full_text)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Could not extract text from PDF: {str(e)}")


def clean_text(text: str) -> str:
    """Clean and normalize extracted PDF text."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = text.strip()
    return text


def validate_pdf(file_bytes: bytes, filename: str) -> None:
    """Validate that the uploaded file is a valid PDF under size limit."""
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_bytes) > max_size:
        raise ValueError("File size must be under 10MB")
    if not filename.lower().endswith('.pdf'):
        raise ValueError("Please upload PDF files only")
    if file_bytes[:5] != b'%PDF-':
        raise ValueError("Please upload PDF files only")
