from app.services.document_generator import generate_docx
from app.services.parser import parse_source
from app.services.pdf_generator import generate_pdf

def test_generators_return_files():
    document = parse_source('https://example.com', 'https://example.com', b'<main><h1>Title</h1><p>Readable content for generated documents.</p></main>')
    assert generate_docx(document).startswith(b'PK')
    assert generate_pdf(document).startswith(b'%PDF')
