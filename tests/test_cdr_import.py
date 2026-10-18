"""Test P3-1: impor .cdr (skip jika tak ada backend)."""
from pathlib import Path
import shutil
import pytest
import utils.cdr_import as cdr


def _backend_available() -> bool:
    t = cdr._which_all()
    return bool(t["cdr2svg"] or t["tracedraw"]) or _has_pylibcdr()


def _has_pylibcdr() -> bool:
    try:
        import pylibcdr  # noqa
        return True
    except ImportError:
        return False


def test_backend_detection():
    t = cdr._which_all()
    assert set(t.keys()) == {"cdr2svg", "cdr2raw", "tracedraw"}


def test_cdr_info_any_file(tmp_path):
    p = tmp_path / "dummy.cdr"
    p.write_bytes(b"RIFF" + b"\x00" * 60)
    info = cdr.cdr_info(p)
    assert info["size_bytes"] == 64
    assert len(info["sha256"]) == 64


@pytest.mark.skipif(not _backend_available(), reason="Tidak ada backend .cdr terpasang")
def test_cdr_to_svg_real(tmp_path):
    pytest.skip("Sediakan file .cdr nyata untuk test")
