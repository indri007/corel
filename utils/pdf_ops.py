"""Operasi PDF dasar: merge, split, rotate, reorder, delete, compress."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)


def merge_pdfs(inputs: Iterable[str | Path], out_pdf: str | Path) -> Path:
    """Gabungkan beberapa PDF jadi satu."""
    out = Path(out_pdf)
    writer = PdfWriter()
    n = 0
    input_list = list(inputs)
    for p in input_list:
        reader = PdfReader(str(p))
        for page in reader.pages:
            writer.add_page(page)
            n += 1
    if n == 0:
        raise ValueError("Tidak ada halaman untuk digabung.")
    with out.open("wb") as f:
        writer.write(f)
    logger.info("Merge %d file → %d halaman → %s", len(input_list), n, out)
    return out


def parse_ranges(spec: str, total: int) -> list[int]:
    """Parse '1-3,5,7-9' → [0,1,2,4,6,7,8] (0-based)."""
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
        else:
            start = end = int(part)
        if start < 1 or end > total or start > end:
            raise ValueError(f"Rentang tidak valid: {part} (total {total})")
        pages.extend(range(start - 1, end))
    if not pages:
        raise ValueError("Rentang kosong.")
    return pages


def extract_pages(src_pdf: str | Path, out_pdf: str | Path, ranges: str) -> Path:
    """Ambil halaman tertentu, contoh ranges='1-3,5'."""
    src, out = Path(src_pdf), Path(out_pdf)
    reader = PdfReader(str(src))
    writer = PdfWriter()
    for i in parse_ranges(ranges, len(reader.pages)):
        writer.add_page(reader.pages[i])
    with out.open("wb") as f:
        writer.write(f)
    return out


def split_pdf(src_pdf: str | Path, outdir: str | Path, chunk: int = 1) -> list[Path]:
    """Pecah PDF jadi beberapa file per chunk halaman."""
    src = Path(src_pdf)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(src))
    outputs: list[Path] = []
    total = len(reader.pages)
    for start in range(0, total, chunk):
        writer = PdfWriter()
        for i in range(start, min(start + chunk, total)):
            writer.add_page(reader.pages[i])
        out = outdir / f"{src.stem}_part{start // chunk + 1:03d}.pdf"
        with out.open("wb") as f:
            writer.write(f)
        outputs.append(out)
    return outputs


def rotate_pdf(src_pdf: str | Path, out_pdf: str | Path, degrees: int = 90) -> Path:
    """Putar semua halaman sebesar degrees (90/180/270)."""
    if degrees % 90 != 0:
        raise ValueError("Rotasi harus kelipatan 90.")
    src, out = Path(src_pdf), Path(out_pdf)
    reader = PdfReader(str(src))
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(degrees)
        writer.add_page(page)
    with out.open("wb") as f:
        writer.write(f)
    return out


def reorder_pdf(src_pdf: str | Path, out_pdf: str | Path, order: str) -> Path:
    """Ubah urutan halaman, contoh order='3,1,2,4'."""
    src, out = Path(src_pdf), Path(out_pdf)
    reader = PdfReader(str(src))
    total = len(reader.pages)
    idx = [int(x.strip()) - 1 for x in order.split(",") if x.strip()]
    if sorted(idx) != list(range(total)):
        raise ValueError(f"Order harus berisi semua halaman 1..{total} tepat sekali.")
    writer = PdfWriter()
    for i in idx:
        writer.add_page(reader.pages[i])
    with out.open("wb") as f:
        writer.write(f)
    return out


def delete_pages(src_pdf: str | Path, out_pdf: str | Path, ranges: str) -> Path:
    """Hapus halaman tertentu, contoh ranges='2,5-7'."""
    src, out = Path(src_pdf), Path(out_pdf)
    reader = PdfReader(str(src))
    total = len(reader.pages)
    to_delete = set(parse_ranges(ranges, total))
    writer = PdfWriter()
    for i in range(total):
        if i not in to_delete:
            writer.add_page(reader.pages[i])
    with out.open("wb") as f:
        writer.write(f)
    return out


def compress_pdf(src_pdf: str | Path, out_pdf: str | Path) -> Path:
    """Kompresi sederhana via pypdf (recompress stream)."""
    src, out = Path(src_pdf), Path(out_pdf)
    reader = PdfReader(str(src))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for page in writer.pages:
        for img in page.images:
            try:
                img.replace(img.image, quality=70)
            except Exception:
                pass
    writer.compress_identical_objects()
    with out.open("wb") as f:
        writer.write(f)
    return out
