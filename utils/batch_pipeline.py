"""Pipeline batch untuk dokumen tebal (tesis, buku 175+ halaman).

Alur:
1. Split per bab (chunk halaman).
2. Opsional: Searchable PDF per bab via make_searchable_pdf.
3. Opsional: Vektorisasi halaman kunci (cover, bagan) via batch_trace.
4. Gabungkan semua output ke satu ZIP rapi.
"""
from __future__ import annotations

import logging
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Callable

from pypdf import PdfReader
import utils.pdf_ops as pops

logger = logging.getLogger(__name__)


def process_thesis(
    src_pdf: str | Path,
    out_zip: str | Path,
    chunk: int = 20,
    do_searchable: bool = False,
    trace_pages: list[int] | None = None,
    trace_centerline: bool = False,
    progress: Callable[[str, int, int], None] | None = None,
) -> Path:
    """Proses PDF tebal menjadi paket ZIP berisi bagian-bagian bab + vektor."""
    src = Path(src_pdf)
    out_z = Path(out_zip)
    if not src.exists():
        raise FileNotFoundError(f"File PDF tidak ditemukan: {src}")

    reader = PdfReader(str(src))
    total_pages = len(reader.pages)

    with tempfile.TemporaryDirectory(prefix="coreldoc_batch_") as td:
        work_dir = Path(td)
        split_dir = work_dir / "bab_pdf"
        split_dir.mkdir()

        # 1. Split
        if progress:
            progress("Split PDF per bab", 0, 1)
        split_files = pops.split_pdf(src, split_dir, chunk=chunk)
        if progress:
            progress("Split PDF per bab", 1, 1)

        # 2. Searchable OCR per part
        final_pdfs = []
        if do_searchable:
            from utils.searchable_pdf import make_searchable_pdf
            ocr_dir = work_dir / "searchable_pdf"
            ocr_dir.mkdir()
            total_parts = len(split_files)
            for idx, part in enumerate(split_files, 1):
                if progress:
                    progress("OCR Searchable", idx, total_parts)
                out_p = ocr_dir / f"searchable_{part.name}"
                try:
                    make_searchable_pdf(part, out_p, lang="ind+eng", deskew=True)
                    final_pdfs.append(out_p)
                except Exception as e:
                    logger.warning("Gagal OCR %s: %s, memakai file split asli", part.name, e)
                    final_pdfs.append(part)
        else:
            final_pdfs = split_files

        # 3. Tracing halaman kunci
        svg_files = []
        if trace_pages:
            import pymupdf
            from PIL import Image
            import io
            from utils.trace_advanced import batch_trace

            trace_dir = work_dir / "vector_svg"
            trace_dir.mkdir()
            img_paths = []

            doc = pymupdf.open(str(src))
            for p_idx in trace_pages:
                if 0 <= p_idx < len(doc):
                    page = doc[p_idx]
                    pix = page.get_pixmap(dpi=150)
                    img_path = trace_dir / f"page_{p_idx+1}.png"
                    img_path.write_bytes(pix.tobytes("png"))
                    img_paths.append(img_path)
            doc.close()

            if img_paths:
                if progress:
                    progress("PowerTRACE Halaman Kunci", 0, len(img_paths))
                svg_files = batch_trace(
                    img_paths,
                    trace_dir,
                    centerline=trace_centerline,
                    remove_bg=True,
                    do_svgo=False
                )
                if progress:
                    progress("PowerTRACE Halaman Kunci", len(img_paths), len(img_paths))

        # 4. ZIP Packaging
        with zipfile.ZipFile(out_z, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in final_pdfs:
                zf.write(p, arcname=f"dokumen_bab/{p.name}")
            for s in svg_files:
                zf.write(s, arcname=f"vektor_halaman/{s.name}")

    logger.info("Batch thesis selesai: %s", out_z)
    return out_z
