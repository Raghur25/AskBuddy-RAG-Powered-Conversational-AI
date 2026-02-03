from pypdf import PdfReader

def load_pdf(file) -> str:
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def load_txt(file) -> str:
    return file.read().decode("utf-8")
