"""
Resume text parser — extracts text from PDF and DOCX files.
"""
import io


def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        import PyPDF2
        text = []
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return '\n'.join(text).strip()
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
        # Also extract from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text.append(cell.text)
        return '\n'.join(text).strip()
    except Exception as e:
        return f"Error extracting DOCX text: {str(e)}"


def extract_resume_text(file_path, file_type):
    """Extract text based on file type."""
    file_type = file_type.lower()
    if file_type == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type == 'docx':
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file type."
