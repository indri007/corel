"""Test P2-3: QR verifikasi + manifest hash."""
from pathlib import Path
import utils.qr_verify as qrv


def test_sha256_stable(tmp_path):
    p = tmp_path / "a.txt"
    p.write_bytes(b"hello")
    assert qrv.sha256_file(p) == qrv.sha256_file(p)
    assert len(qrv.sha256_file(p)) == 64


def test_manifest_and_qr(tmp_path):
    p = tmp_path / "doc.pdf"
    p.write_bytes(b"%PDF-1.4\n")
    man = qrv.make_manifest(p, "DOC-1", "https://example.com")
    assert man["sha256"] == qrv.sha256_file(p)
    assert "verify/DOC-1" in man["url"]
    qr = qrv.make_qr(man["url"], tmp_path / "qr.png")
    assert qr.exists() and qr.stat().st_size > 100
