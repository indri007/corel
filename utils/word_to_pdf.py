import subprocess
import tempfile
import os
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def check_libreoffice_installed() -> bool:
    """Memeriksa apakah binari soffice (LibreOffice) tersedia di sistem PATH."""
    return shutil.which("soffice") is not None

def word_to_pdf(src_path: str, output_dir: Optional[str] = None) -> str:
    """
    Mengonversi dokumen Word (.doc, .docx), OpenDocument (.odt), Rich Text (.rtf), 
    atau teks (.txt) menjadi berkas PDF dengan fidelity penuh (preservasi tata letak, 
    gambar, tabel, font, dan header/footer) menggunakan LibreOffice headless mode.

    Args:
        src_path (str): Path lengkap berkas dokumen sumber.
        output_dir (Optional[str]): Direktori output. Jika None, dibuatkan direktori sementara.

    Returns:
        str: Path absolut berkas PDF hasil konversi.

    Raises:
        FileNotFoundError: Jika berkas sumber tidak ditemukan atau soffice tidak terpasang.
        RuntimeError: Jika proses konversi LibreOffice mengembalikan kode galat atau timeout.
    """
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Berkas sumber tidak ditemukan: {src_path}")

    soffice_bin = shutil.which("soffice")
    if not soffice_bin:
        raise FileNotFoundError(
            "LibreOffice ('soffice') tidak ditemukan di sistem PATH.\n"
            "Silakan instal LibreOffice:\n"
            "  - macOS: brew install --cask libreoffice\n"
            "  - Ubuntu/Debian: sudo apt update && sudo apt install -y libreoffice\n"
            "  - Docker: sertakan 'libreoffice' pada paket apt."
        )

    target_dir = output_dir or tempfile.mkdtemp(prefix="coreldoc_lo_")
    os.makedirs(target_dir, exist_ok=True)

    cmd = [
        soffice_bin,
        "--headless",
        "--norestore",
        "--invisible",
        "--convert-to", "pdf",
        "--outdir", target_dir,
        src_path
    ]

    logger.info(f"Menjalankan konversi Word->PDF: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180
        )
        if result.returncode != 0:
            err_msg = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Eksekusi soffice gagal (kode {result.returncode}): {err_msg}")
            raise RuntimeError(f"Gagal mengonversi via LibreOffice: {err_msg}")

        base_name = os.path.splitext(os.path.basename(src_path))[0] + ".pdf"
        pdf_path = os.path.join(target_dir, base_name)

        if not os.path.exists(pdf_path):
            raise RuntimeError(f"Berkas PDF tidak ditemukan pada direktori target: {pdf_path}")

        logger.info(f"Konversi berhasil: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
        return pdf_path

    except subprocess.TimeoutExpired as exc:
        logger.error(f"Proses konversi soffice timeout setelah 180 detik: {src_path}")
        raise RuntimeError("Proses konversi dokumen Word melebihi batas waktu (timeout 180 detik).") from exc
