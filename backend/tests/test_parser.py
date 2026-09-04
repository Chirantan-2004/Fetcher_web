from pathlib import Path
from app.services.parser import parse_source

def test_parser_preserves_content_and_removes_noise():
    raw = Path('backend/tests/fixtures/article.html').read_bytes()
    document = parse_source('https://example.com/article', 'https://example.com/article', raw)
    assert document.title == 'Research Notes'
    assert document.author == 'A. Writer'
    assert document.statistics.word_count > 5
    blocks = [block for section in document.content['sections'] for block in section.blocks]
    assert any(block.type == 'list' for block in blocks)
    assert any(block.type == 'table' for block in blocks)
