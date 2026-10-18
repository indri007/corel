"""Buat Searchable PDF: PDF asli + layer teks OCR yang bisa dicari/di-copy."""
from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def make_searchable_pdf(
    src_pdf: str | Path,
    out_pdf: str | Path,
    lang: str = "ind+eng",
    deskew: bool = True,
    force_ocr: bool = False,
) -> Path:
    """Konversi PDF ke Searchable PDF via ocrmypdf.

    Args:
        src_pdf: Path PDF sumber (bisa hasil scan atau PDF digital).
        out_pdf: Path PDF output.
        lang: Kode bahasa Tesseract, contoh "ind", "eng", "ind+eng".
        deskew: Auto-deskew halaman scan.
        force_ocr: Paksa OCR walau sudah ada layer teks.

    Returns:
        Path ke PDF output.

    Raises:
        RuntimeError: Jika ocrmypdf gagal.
        FileNotFoundError: Jika file sumber tidak ada.
    """
    src = Path(src_pdf)
    out = Path(out_pdf)
    if not src.exists():
        raise FileNotFoundError(f"PDF sumber tidak ditemukan: {src}")
    if shutil.which("ocrmypdf") is None:
        raise RuntimeError(
            "ocrmypdf tidak terpasang. Jalankan: pip install ocrmypdf && "
            "brew install tesseract-lang"
        )

    cmd = ["ocrmypdf", "--language", lang, "--output-type", "pdfa-2"]
    if deskew:
        cmd.append("--deskew")
    if force_ocr:
        cmd.append("--force-ocr")
    else:
        cmd.append("--skip-text")
    cmd += [str(src), str(out)]

    logger.info("Menjalankan: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if result.returncode != 0:
        raise RuntimeError(
            f"ocrmypdf gagal (exit {result.returncode}):\n"
            f"stdout: {result.stdout.strip()[-800:]}\n"
            f"stderr: {result.stderr.strip()[-800:]}"
        )
    if not out.exists():
        raise RuntimeError(f"Output tidak ditemukan: {out}")
    return out


def ocr_langs_available() -> list[str]:
    """Kembalikan daftar bahasa Tesseract yang terpasang."""
    try:
        r = subprocess.run(
            ["tesseract", "--list-langs"],
            capture_output=True, text=True, timeout=10,
        )
        return [
            ln.strip() for ln in r.stdout.splitlines()
            if ln.strip() and "available" not in ln.lower()
        ]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def create_searchable_pdf(
    input_pdf_bytes: bytes,
    lang: str = "ind+eng",
    deskew: bool = True
) -> bytes:
    """Wrapper bytes-to-bytes untuk kompatibilitas Streamlit & test suite."""
    with tempfile.TemporaryDirectory(prefix="coreldoc_s_") as tmpdir:
        in_path = Path(tmpdir) / "in.pdf"
        out_path = Path(tmpdir) / "out.pdf"
        in_path.write_bytes(input_pdf_bytes)

        make_searchable_pdf(in_path, out_path, lang=lang, deskew=deskew)
        return out_path.read_bytes()
