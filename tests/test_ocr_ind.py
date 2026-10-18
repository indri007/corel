"""Test OCR dengan bahasa Indonesia."""
from pathlib import Path
import subprocess
import pytest
from PIL import Image, ImageDraw
import pytesseract


@pytest.fixture
def sample_text_png(tmp_path: Path) -> Path:
    img = Image.new("RGB", (600, 160), "white")
    ImageDraw.Draw(img).text((20, 60), "TES INDONESIA", fill="black")
    p = tmp_path / "text.png"
    img.save(p)
    return p


def test_ocr_ind_lang(sample_text_png):
    langs = pytesseract.get_languages(config="")
    if "ind" not in langs:
        pytest.skip("tesseract-ocr-ind belum terpasang")
    txt = pytesseract.image_to_string(Image.open(sample_text_png), lang="ind").upper()
    assert "INDONESIA" in txt or "TES" in txt
