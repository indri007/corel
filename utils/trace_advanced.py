"""Vektorisasi produksi: VTracer (warna) / Potrace (centerline) + optimasi SVG."""
from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)


def remove_background(img_path: str | Path, threshold: int = 240) -> Path:
    """Hapus latar putih → transparan sebelum tracing."""
    src = Path(img_path)
    img = Image.open(src).convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r >= threshold and g >= threshold and b >= threshold:
                px[x, y] = (r, g, b, 0)
    out = src.with_name(src.stem + "_nobg.png")
    img.save(out, "PNG")
    return out


def trace_color_vtracer(img_path: str | Path, out_svg: str | Path,
                        n_colors: int = 6, mode: str = "spline") -> Path:
    """Tracing warna via vtracer."""
    import vtracer
    out = Path(out_svg)
    vtracer.convert_image_to_svg_py(
        str(img_path), str(out),
        colormode="color", hierarchical="stacked", mode=mode,
        filter_speckle=4, color_precision=6, layer_difference=16,
        corner_threshold=60, length_threshold=4.0, max_iterations=10,
        splice_threshold=45, path_precision=8,
    )
    logger.info("VTracer → %s", out)
    return out


def trace_centerline_potrace(img_path: str | Path, out_svg: str | Path) -> Path:
    """Tracing centerline via potrace (untuk tanda tangan, line art, ukiran)."""
    if shutil.which("potrace") is None:
        raise RuntimeError("potrace tidak terpasang. Jalankan: brew install potrace")
    src, out = Path(img_path), Path(out_svg)
    # potrace mendukung bitmap BMP secara native
    with tempfile.TemporaryDirectory() as td:
        bmp = Path(td) / "in.bmp"
        Image.open(src).convert("L").point(lambda v: 0 if v < 128 else 255, "1").save(bmp, "BMP")
        cmd = ["potrace", str(bmp), "-s", "-o", str(out), "--flat"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            raise RuntimeError(f"potrace gagal: {r.stderr.strip()[-500:]}")
    logger.info("Potrace centerline → %s", out)
    return out


def optimize_svg(svg_in: str | Path, svg_out: str | Path | None = None) -> Path:
    """Optimasi SVG via svgo jika tersedia, jika tidak copy apa adanya."""
    src = Path(svg_in)
    out = Path(svg_out) if svg_out else src.with_name(src.stem + "_min.svg")
    if shutil.which("svgo") is not None:
        r = subprocess.run(
            ["svgo", "-i", str(src), "-o", str(out), "--multipass"],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode == 0 and out.exists():
            logger.info("SVGO → %s", out)
            return out
    shutil.copy(src, out)
    return out


def batch_trace(
    images: list[str | Path],
    outdir: str | Path,
    engine: str = "vtracer",
    centerline: bool = False,
    remove_bg: bool = False,
    do_svgo: bool = True,
    progress=None,
) -> list[Path]:
    """Batch tracing. progress: callable(step, total) untuk Streamlit."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    results: list[Path] = []
    total = len(images)
    for i, img in enumerate(images, 1):
        src = Path(img)
        work = remove_background(src) if remove_bg else src
        svg = outdir / (src.stem + ".svg")
        if centerline or engine == "potrace":
            trace_centerline_potrace(work, svg)
        else:
            trace_color_vtracer(work, svg)
        if do_svgo:
            svg = optimize_svg(svg)
        results.append(svg)
        if progress:
            progress(i, total)
    return results
