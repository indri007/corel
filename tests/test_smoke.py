"""Smoke test minimal untuk CorelDoc Studio."""
from utils.word_to_pdf import word_to_pdf

def test_word_to_pdf_callable():
    assert callable(word_to_pdf)

def test_word_to_pdf_signature():
    import inspect
    sig = inspect.signature(word_to_pdf)
    assert "src_path" in sig.parameters
