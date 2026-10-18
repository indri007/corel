"""Impor file CorelDRAW (.cdr) ke format yang bisa diproses.

Fallback berantai:
1. libcdr via cdr2svg / cdr2raw (jika terpasang via brew/apt)
2. TraceDraw binary (jika di-clone dan di-build)
3. pylibcdr (Python binding)
4. Gagal dengan pesan jelas
"""
from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def _which_all() -> dict[str, str | None]:
    """Deteksi tool .cdr yang tersedia di sistem."""
    return {
        "cdr2svg": shutil.which("cdr2svg"),
        "cdr2raw": shutil.which("cdr2raw"),
        "tracedraw": shutil.which("tracedraw"),
    }


def cdr_to_svg(src_cdr: str | Path, out_svg: str | Path) -> Path:
    """Konversi .cdr → .svg via rantai fallback.

    Args:
        src_cdr: Path file .cdr.
        out_svg: Path file .svg output.

    Returns:
        Path ke .svg hasil.

    Raises:
        RuntimeError: Jika semua backend gagal.
    """
    src, out = Path(src_cdr), Path(out_svg)
    if not src.exists():
        raise FileNotFoundError(f"File CDR tidak ditemukan: {src}")

    tools = _which_all()
    errors: list[str] = []

    # 1. cdr2svg (dari libcdr)
    if tools["cdr2svg"]:
        try:
            r = subprocess.run(
                [tools["cdr2svg"], str(src), str(out)],
                capture_output=True, text=True, timeout=300,
            )
            if r.returncode == 0 and out.exists():
                logger.info("CDR → SVG via cdr2svg")
                return out
            errors.append(f"cdr2svg: {r.stderr.strip()[-300:]}")
        except Exception as e:
            errors.append(f"cdr2svg: {e}")

    # 2. TraceDraw (kalau di-build dari repo)
    if tools["tracedraw"]:
        try:
            r = subprocess.run(
                [tools["tracedraw"], "--export-svg", str(out), str(src)],
                capture_output=True, text=True, timeout=300,
            )
            if r.returncode == 0 and out.exists():
                logger.info("CDR → SVG via tracedraw")
                return out
            errors.append(f"tracedraw: {r.stderr.strip()[-300:]}")
        except Exception as e:
            errors.append(f"tracedraw: {e}")

    # 3. pylibcdr (Python binding)
    try:
        import pylibcdr  # type: ignore
        with src.open("rb") as f:
            doc = pylibcdr.parse(f.read())
        with out.open("w", encoding="utf-8") as f:
            f.write(doc.to_svg())
        logger.info("CDR → SVG via pylibcdr")
        return out
    except ImportError:
        errors.append("pylibcdr: tidak terpasang")
    except Exception as e:
        errors.append(f"pylibcdr: {e}")

    raise RuntimeError(
        "Semua backend .cdr gagal. Instal salah satu:\n"
        "  brew install libcdr           (macOS)\n"
        "  sudo apt install libcdr-tools (Linux)\n"
        "  pip install pylibcdr\n"
        "  atau build TraceDraw dari repo igtoth/tracedraw\n\n"
        f"Detail error:\n  - " + "\n  - ".join(errors)
    )


def cdr_to_png(src_cdr: str | Path, out_png: str | Path, dpi: int = 300) -> Path:
    """Konversi .cdr → .png (via SVG intermediate)."""
    import cairosvg
    svg = Path(out_png).with_suffix(".svg")
    cdr_to_svg(src_cdr, svg)
    cairosvg.svg2png(url=str(svg), write_to=str(out_png), dpi=dpi)
    svg.unlink(missing_ok=True)
    logger.info("CDR → PNG %d DPI → %s", dpi, out_png)
    return Path(out_png)


def cdr_to_pdf(src_cdr: str | Path, out_pdf: str | Path) -> Path:
    """Konversi .cdr → .pdf (via SVG → PDF)."""
    import cairosvg
    svg = Path(out_pdf).with_suffix(".svg")
    cdr_to_svg(src_cdr, svg)
    cairosvg.svg2pdf(url=str(svg), write_to=str(out_pdf))
    svg.unlink(missing_ok=True)
    logger.info("CDR → PDF → %s", out_pdf)
    return Path(out_pdf)


def cdr_info(src_cdr: str | Path) -> dict:
    """Info ringkas file .cdr (hash, ukuran, versi jika terdeteksi)."""
    from utils.qr_verify import sha256_file
    p = Path(src_cdr)
    data = p.read_bytes()[:16]
    version = "unknown"
    if data[:2] == b"RI":
        try:
            version = f"v{int.from_bytes(data[2:4], 'little')}"
        except Exception:
            pass
    return {
        "filename": p.name,
        "size_bytes": p.stat().st_size,
        "sha256": sha256_file(p),
        "detected_version": version,
    }
