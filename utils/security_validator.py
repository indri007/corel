import os
import mimetypes
import logging
from typing import Tuple, List, Optional
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

# Batas ukuran berkas 50 MB (dalam bytes)
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 52,428,800 bytes

ALLOWED_MIME_TYPES = {
    # Dokumen PDF
    "pdf": ["application/pdf"],
    # Dokumen Word & OpenDocument
    "docx": [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip"
    ],
    "doc": [
        "application/msword",
        "application/x-msword"
    ],
    "odt": ["application/vnd.oasis.opendocument.text"],
    "rtf": ["application/rtf", "text/rtf"],
    "txt": ["text/plain"],
    # Format Gambar
    "png": ["image/png"],
    "jpg": ["image/jpeg"],
    "jpeg": ["image/jpeg"],
    "webp": ["image/webp"],
    "svg": ["image/svg+xml", "text/xml", "application/xml"]
}

MAGIC_HEADER_SIGNATURES = {
    b"%PDF": "pdf",
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpeg",
    b"RIFF": "webp",
    b"PK\x03\x04": "zip_docx",  # .docx adalah zip container
    b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1": "ole_doc",  # .doc lama format OLE CFB
}

def sanitize_and_validate_file(
    file_bytes: bytes,
    original_filename: str,
    allowed_extensions: List[str],
    max_size_bytes: int = MAX_FILE_SIZE_BYTES
) -> Tuple[bool, str, str]:
    """
    Melakukan sanitasi nama berkas, validasi batas ukuran (50MB), dan inspeksi MIME/Magic bytes.

    Args:
        file_bytes (bytes): Konten biner dari berkas yang diunggah.
        original_filename (str): Nama asli berkas dari uploader.
        allowed_extensions (List[str]): Daftar ekstensi yang diizinkan (misal: ['pdf', 'docx']).
        max_size_bytes (int): Ukuran maksimum yang diizinkan (default 50MB).

    Returns:
        Tuple[bool, str, str]: (is_valid, safe_filename, message)
    """
    safe_name = secure_filename(original_filename)
    if not safe_name:
        safe_name = "dokumen_upload"

    file_size = len(file_bytes)
    if file_size == 0:
        return False, safe_name, "Berkas kosong (0 bytes)."

    if file_size > max_size_bytes:
        mb_actual = file_size / (1024 * 1024)
        mb_limit = max_size_bytes / (1024 * 1024)
        logger.warning(f"Berkas ditolak karena melebihi batas: {safe_name} ({mb_actual:.2f} MB > {mb_limit:.0f} MB)")
        return False, safe_name, f"Ukuran berkas ({mb_actual:.2f} MB) melebihi batas maksimum {mb_limit:.0f} MB."

    ext = os.path.splitext(safe_name)[1].lower().lstrip(".")
    if not ext or ext not in [e.lower() for e in allowed_extensions]:
        allowed_str = ", ".join(allowed_extensions)
        return False, safe_name, f"Format berkas '.{ext}' tidak diizinkan. Format yang didukung: {allowed_str}"

    # Verifikasi Magic Bytes header untuk pencegahan MIME spoofing
    if ext == "pdf" and not file_bytes.startswith(b"%PDF"):
        return False, safe_name, "Header berkas bukan format PDF valid (Magic bytes mismatch)."
    elif ext in ("png",) and not file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return False, safe_name, "Header berkas bukan format PNG valid."
    elif ext in ("jpg", "jpeg") and not file_bytes.startswith(b"\xff\xd8\xff"):
        return False, safe_name, "Header berkas bukan format JPEG valid."
    elif ext == "docx" and not file_bytes.startswith(b"PK\x03\x04"):
        return False, safe_name, "Header berkas bukan berkas DOCX valid (ZIP header mismatch)."

    logger.info(f"Validasi berkas sukses: {safe_name} ({file_size} bytes)")
    return True, safe_name, "Berkas valid."
