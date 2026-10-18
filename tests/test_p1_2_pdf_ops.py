"""Test P1-2: Operasi PDF."""
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import pytest
import utils.pdf_ops as pops


def _make_pdf(path: Path, n: int) -> Path:
    w = PdfWriter()
    for _ in range(n):
        w.add_blank_page(width=200, height=200)
    with path.open("wb") as f:
        w.write(f)
    return path


def test_merge(tmp_path):
    a = _make_pdf(tmp_path / "a.pdf", 2)
    b = _make_pdf(tmp_path / "b.pdf", 3)
    out = pops.merge_pdfs([a, b], tmp_path / "m.pdf")
    assert len(PdfReader(out).pages) == 5


def test_extract(tmp_path):
    src = _make_pdf(tmp_path / "s.pdf", 5)
    out = pops.extract_pages(src, tmp_path / "e.pdf", "1-2,5")
    assert len(PdfReader(out).pages) == 3


def test_split(tmp_path):
    src = _make_pdf(tmp_path / "s.pdf", 5)
    outs = pops.split_pdf(src, tmp_path / "parts", chunk=2)
    assert len(outs) == 3


def test_rotate(tmp_path):
    src = _make_pdf(tmp_path / "s.pdf", 2)
    out = pops.rotate_pdf(src, tmp_path / "r.pdf", 90)
    assert len(PdfReader(out).pages) == 2


def test_reorder(tmp_path):
    src = _make_pdf(tmp_path / "s.pdf", 3)
    out = pops.reorder_pdf(src, tmp_path / "o.pdf", "3,1,2")
    assert len(PdfReader(out).pages) == 3


def test_delete(tmp_path):
    src = _make_pdf(tmp_path / "s.pdf", 5)
    out = pops.delete_pages(src, tmp_path / "d.pdf", "2,4-5")
    assert len(PdfReader(out).pages) == 2


def test_parse_ranges_invalid():
    with pytest.raises(ValueError):
        pops.parse_ranges("0-3", total=5)
    with pytest.raises(ValueError):
        pops.parse_ranges("1-10", total=5)
