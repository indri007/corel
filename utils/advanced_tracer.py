import io
import os
import shutil
import tempfile
import logging
import subprocess
from typing import Optional, List, Tuple
from PIL import Image, ImageOps
import numpy as np
import vtracer

logger = logging.getLogger(__name__)

def remove_background_threshold(image: Image.Image, threshold: int = 240) -> Image.Image:
    """
    Menghapus latar belakang putih/terang sebelum proses tracing dengan mengubahnya menjadi transparan (RGBA).
    Sangat esensial untuk vektorisasi tanda tangan, stempel, dan logo.
    """
    img_rgba = image.convert("RGBA")
    np_img = np.array(img_rgba)

    r, g, b, a = np_img[:, :, 0], np_img[:, :, 1], np_img[:, :, 2], np_img[:, :, 3]
    # Piksel di atas threshold putih dianggap sebagai background dan dijadikan alpha 0
    is_white = (r >= threshold) & (g >= threshold) & (b >= threshold)
    np_img[is_white, 3] = 0

    return Image.fromarray(np_img, mode="RGBA")

def potrace_centerline_trace(image: Image.Image) -> Optional[str]:
    """
    Tracing garis tengah (Centerline Tracing) menggunakan binari potrace / autotrace jika tersedia.
    Cocok untuk sketsa garis, diagram alir, dan tanda tangan tulisan tangan.
    """
    potrace_bin = shutil.which("potrace")
    if not potrace_bin:
        return None

    with tempfile.TemporaryDirectory(prefix="coreldoc_potrace_") as tmpdir:
        bmp_path = os.path.join(tmpdir, "input.bmp")
        svg_path = os.path.join(tmpdir, "output.svg")

        # Binarize ke mode 1-bit hitam putih
        gray = image.convert("L")
        bw = gray.point(lambda x: 0 if x < 180 else 255, mode="1")
        bw.save(bmp_path)

        cmd = [potrace_bin, "-s", "-o", svg_path, bmp_path]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0 and os.path.exists(svg_path):
                with open(svg_path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Potrace execution failed: {e}")

    return None

def optimize_svg_output(svg_code: str) -> Tuple[str, bool]:
    """
    Mengoptimalkan dan merampingkan kode SVG menggunakan svgo atau oxvg jika terinstal.
    Jika tidak tersedia, mengembalikan SVG asli tanpa kompromi integritas.
    """
    tool_bin = shutil.which("svgo") or shutil.which("oxvg")
    if not tool_bin:
        return svg_code, False

    with tempfile.TemporaryDirectory(prefix="coreldoc_svgopt_") as tmpdir:
        in_svg = os.path.join(tmpdir, "in.svg")
        out_svg = os.path.join(tmpdir, "out.svg")

        with open(in_svg, "w", encoding="utf-8") as f:
            f.write(svg_code)

        if "svgo" in tool_bin:
            cmd = [tool_bin, in_svg, "-o", out_svg]
        else:
            cmd = [tool_bin, in_svg, out_svg]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if res.returncode == 0 and os.path.exists(out_svg):
                with open(out_svg, "r", encoding="utf-8") as f_out:
                    return f_out.read(), True
        except Exception as e:
            logger.warning(f"SVG Optimizer {tool_bin} gagal: {e}")

    return svg_code, False

def advanced_vectorize_image(
    image: Image.Image,
    mode: str = "spline",
    colormode: str = "color",
    hierarchical: str = "stacked",
    filter_speckle: int = 4,
    color_precision: int = 6,
    layer_difference: int = 16,
    corner_threshold: int = 60,
    length_threshold: float = 4.0,
    max_iterations: int = 10,
    remove_bg: bool = False,
    optimize_svg: bool = True
) -> str:
    """
    Pipeline PowerTRACE Vektor Tingkat Produksi:
    1. Penghapusan Latar Belakang Cerdas (Opsional).
    2. Vektor Tracing VTracer Multi-warna dan Kurva Bézier Presisi Tinggi.
    3. Centerline Tracing Fallback jika mode 'centerline' dipilih.
    4. Optimasi Pasca-Tracing (SVGO/oxvg).
    """
    processed_img = image
    if remove_bg:
        processed_img = remove_background_threshold(image)

    # Deteksi jika pengguna meminta centerline tracing
    if mode == "centerline":
        centerline_svg = potrace_centerline_trace(processed_img)
        if centerline_svg:
            if optimize_svg:
                centerline_svg, _ = optimize_svg_output(centerline_svg)
            return centerline_svg
        logger.info("Potrace tidak ditemukan, melanjutkan dengan VTracer mode kurva presisi.")
        mode = "spline"

    # Konversi Pillow Image ke file sementara untuk input vtracer
    with tempfile.TemporaryDirectory(prefix="coreldoc_vtracer_") as tmpdir:
        input_img_path = os.path.join(tmpdir, "source.png")
        output_svg_path = os.path.join(tmpdir, "vectorized.svg")

        processed_img.save(input_img_path, format="PNG")

        vtracer.convert_image_to_svg_py(
            input_img_path,
            output_svg_path,
            colormode=colormode,
            hierarchical=hierarchical,
            mode=mode,
            filter_speckle=filter_speckle,
            color_precision=color_precision,
            layer_difference=layer_difference,
            corner_threshold=corner_threshold,
            length_threshold=length_threshold,
            max_iterations=max_iterations,
            splice_threshold=45,
            path_precision=3
        )

        with open(output_svg_path, "r", encoding="utf-8") as f_svg:
            raw_svg = f_svg.read()

        if optimize_svg:
            optimized_svg, was_opt = optimize_svg_output(raw_svg)
            return optimized_svg

        return raw_svg
