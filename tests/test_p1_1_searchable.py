"""Test P1-1: Searchable PDF."""
from pathlib import Path
import subprocess
import pytest
from pypdf import PdfReader


@pytest.fixture
def sample_scanned_pdf(tmp_path: Path) -> Path:
    """Buat PDF 'scan' sederhana dari gambar teks via PIL."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (800, 200), "white")
    d = ImageDraw.Draw(img)
    d.text((40, 80), "HELLO OCR WORLD", fill="black")
    pdf = tmp_path / "scan.pdf"
    img.save(pdf, "PDF", resolution=150.0)
    return pdf


def test_ocrmypdf_available():
    assert subprocess.run(["which", "ocrmypdf"], capture_output=True).returncode == 0


def test_searchable_pdf_has_text(sample_scanned_pdf, tmp_path):
    from utils.searchable_pdf import make_searchable_pdf
    out = tmp_path / "out.pdf"
    make_searchable_pdf(sample_scanned_pdf, out, lang="eng", deskew=True)
    assert out.exists() and out.stat().st_size > 0
    reader = PdfReader(str(out))
    text = (reader.pages[0].extract_text() or "").upper()
    assert "HELLO" in text or "OCR" in text
