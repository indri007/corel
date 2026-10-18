import io
import hashlib
from typing import Optional
from PIL import Image
import pymupdf
import streamlit as st

@st.cache_data(show_spinner=False)
def get_cached_pdf_page_image(pdf_bytes: bytes, page_number: int, dpi: int = 150) -> Image.Image:
    """
    Render halaman PDF menjadi PIL Image dengan caching efisien berdasarkan konten biner, nomor halaman, dan DPI.
    Mencegah komputasi rasterisasi berulang saat pengguna berinteraksi dengan widget Streamlit.
    """
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    if page_number < 1 or page_number > len(doc):
        raise ValueError(f"Halaman {page_number} berada di luar rentang (Total: {len(doc)}).")

    page = doc[page_number - 1]
    zoom = dpi / 72.0
    matrix = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    doc.close()
    return img

@st.cache_data(show_spinner=False)
def get_cached_pdf_page_count(pdf_bytes: bytes) -> int:
    """Mengembalikan total halaman PDF dengan caching."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    total = len(doc)
    doc.close()
    return total

@st.cache_data(show_spinner=False)
def compute_sha256(data: bytes) -> str:
    """Menghitung hash SHA-256 dokumen untuk keperluan audit keaslian."""
    return hashlib.sha256(data).hexdigest()
