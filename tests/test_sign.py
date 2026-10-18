"""Test P2-2: tanda tangan digital PAdES."""
from pathlib import Path
import pytest
from reportlab.pdfgen import canvas
import utils.sign as signlib


def _pdf(p: Path) -> Path:
    c = canvas.Canvas(str(p))
    c.drawString(100, 700, "DOC")
    c.save()
    return p


def test_roundtrip_sign_verify(tmp_path):
    try:
        import pyhanko  # noqa
    except ImportError:
        pytest.skip("pyhanko belum terpasang")
    src = _pdf(tmp_path / "in.pdf")
    cert, key = signlib.generate_self_signed_cert(tmp_path / "c.pem", tmp_path / "k.pem")
    out = signlib.sign_pdf(src, tmp_path / "out.pdf", key, cert)
    assert out.exists()
    res = signlib.verify_signature(out)
    assert res["count"] >= 1
    assert res["signatures"][0].get("intact") is True
