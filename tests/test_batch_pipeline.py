"""Test P3-4: batch pipeline (tanpa OCR/trace untuk kecepatan)."""
from pathlib import Path
import zipfile
import pytest
from pypdf import PdfWriter
import utils.batch_pipeline as bp


def _make_pdf(p: Path, n: int) -> Path:
    w = PdfWriter()
    for _ in range(n):
        w.add_blank_page(width=100, height=100)
    with p.open("wb") as f:
        w.write(f)
    return p


def test_pipeline_split_only(tmp_path):
    src = _make_pdf(tmp_path / "in.pdf", 25)
    out = bp.process_thesis(src, tmp_path / "out.zip", chunk=10,
                            do_searchable=False, trace_pages=None)
    assert out.exists()
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
    assert len(names) == 3  # 10 + 10 + 5
    assert all(n.endswith(".pdf") for n in names)


def test_pipeline_progress_callback(tmp_path):
    src = _make_pdf(tmp_path / "in.pdf", 15)
    calls = []
    bp.process_thesis(src, tmp_path / "out.zip", chunk=10,
                     do_searchable=False, trace_pages=None,
                     progress=lambda s, c, t: calls.append((s, c, t)))
    assert any("Split" in c[0] for c in calls)
