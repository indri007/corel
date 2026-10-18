"""Test P2-1: redaksi PDF."""
from pathlib import Path
import pytest
from pypdf import PdfWriter, PdfReader
import utils.redact as redact


def _make_text_pdf(path: Path, text: str = "SECRET") -> Path:
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(path))
    c.drawString(100, 700, text)
    c.save()
    return path


def test_redact_rect(tmp_path):
    src = _make_text_pdf(tmp_path / "in.pdf")
    out = redact.redact_rect(src, tmp_path / "out.pdf", 0, (80, 680, 250, 720))
    assert out.exists() and out.stat().st_size > 0
    assert len(PdfReader(str(out)).pages) == 1


def test_redact_rect_invalid_page(tmp_path):
    src = _make_text_pdf(tmp_path / "in.pdf")
    with pytest.raises(IndexError):
        redact.redact_rect(src, tmp_path / "out.pdf", 5, (0, 0, 10, 10))


def test_redact_text_not_found(tmp_path):
    src = _make_text_pdf(tmp_path / "in.pdf", "PUBLIC")
    with pytest.raises(ValueError):
        redact.redact_text(src, tmp_path / "out.pdf", "NOTHING")
