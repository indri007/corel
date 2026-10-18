import io
import os
import tempfile
import logging
import subprocess
from typing import List, Optional
import pypdf
import pymupdf

logger = logging.getLogger(__name__)

def merge_pdfs(pdf_bytes_list: List[bytes]) -> bytes:
    """
    Menggabungkan beberapa dokumen PDF menjadi satu berkas terpadu menggunakan pypdf.PdfWriter.
    """
    writer = pypdf.PdfWriter()
    for idx, pdf_b in enumerate(pdf_bytes_list):
        reader = pypdf.PdfReader(io.BytesIO(pdf_b))
        for page in reader.pages:
            writer.add_page(page)
    out_buf = io.BytesIO()
    writer.write(out_buf)
    writer.close()
    return out_buf.getvalue()

def split_pdf_by_ranges(pdf_bytes: bytes, page_ranges_str: str) -> bytes:
    """
    Memecah / mengekstrak halaman PDF berdasarkan string rentang (misal: '1-3, 5, 8-10').
    Halaman berbasis 1-indexed.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    writer = pypdf.PdfWriter()
    total_pages = len(reader.pages)

    target_indices = []
    parts = [p.strip() for p in page_ranges_str.split(",") if p.strip()]

    for part in parts:
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = max(1, int(start_str.strip()))
            end = min(total_pages, int(end_str.strip()))
            target_indices.extend(range(start - 1, end))
        else:
            idx = int(part.strip())
            if 1 <= idx <= total_pages:
                target_indices.append(idx - 1)

    # Hilangkan duplikasi dengan tetap menjaga urutan
    seen = set()
    unique_indices = []
    for idx in target_indices:
        if idx not in seen:
            seen.add(idx)
            unique_indices.append(idx)

    for idx in unique_indices:
        writer.add_page(reader.pages[idx])

    out_buf = io.BytesIO()
    writer.write(out_buf)
    writer.close()
    return out_buf.getvalue()

def rotate_pdf_pages(pdf_bytes: bytes, angle: int, page_selection: str = "all") -> bytes:
    """
    Memutar orientasi halaman PDF (90, 180, 270 derajat searah jarum jam).
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    writer = pypdf.PdfWriter()

    total = len(reader.pages)
    for i in range(total):
        page = reader.pages[i]
        if page_selection == "all":
            page.rotate(angle)
        writer.add_page(page)

    out_buf = io.BytesIO()
    writer.write(out_buf)
    writer.close()
    return out_buf.getvalue()

def reorder_and_delete_pages(pdf_bytes: bytes, page_order_1indexed: List[int]) -> bytes:
    """
    Menyusun ulang urutan halaman atau menghapus halaman yang tidak disertakan dalam daftar.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    writer = pypdf.PdfWriter()
    total = len(reader.pages)

    for p_num in page_order_1indexed:
        if 1 <= p_num <= total:
            writer.add_page(reader.pages[p_num - 1])

    out_buf = io.BytesIO()
    writer.write(out_buf)
    writer.close()
    return out_buf.getvalue()

def compress_optimize_pdf(pdf_bytes: bytes) -> bytes:
    """
    Mengompresi dan mengoptimalkan struktur PDF (kompresi stream gambar & penghapusan duplikasi objek).
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    writer = pypdf.PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)

    out_buf = io.BytesIO()
    writer.write(out_buf)
    writer.close()
    return out_buf.getvalue()
