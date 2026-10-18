import io
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

def clean_scanned_document(image: Image.Image, aggressiveness: float = 1.2) -> Image.Image:
    """
    Mengoptimalkan hasil scan dokumen/tulisan agar terlihat bersih dan profesional:
    - Memutihkan latar belakang kertas kotor/berbintik.
    - Menghitamkan dan menajamkan teks tulisan.
    """
    # 1. Konversi ke Grayscale
    gray = image.convert("L")

    # 2. Penajaman teks
    sharpened = gray.filter(ImageFilter.UnsharpMask(radius=2, percent=160, threshold=3))

    # 3. Normalisasi level (Auto-Contrast)
    autocontrast = ImageOps.autocontrast(sharpened, cutoff=2)

    # 4. White-point leveling dengan numpy untuk hasil ultra-clean
    np_img = np.array(autocontrast, dtype=np.float32)

    # Adaptive background whitening
    # Nilai di atas threshold diangkat menjadi putih sempurna (255)
    high_cutoff = 220 - (aggressiveness * 20)
    low_cutoff = 70 + (aggressiveness * 15)

    np_img = (np_img - low_cutoff) / (high_cutoff - low_cutoff) * 255.0
    np_img = np.clip(np_img, 0, 255).astype(np.uint8)

    clean_img = Image.fromarray(np_img)
    return clean_img.convert("RGB")

def enhance_photo_professional(
    image: Image.Image,
    brightness: float = 1.05,
    contrast: float = 1.2,
    sharpness: float = 1.4,
    color: float = 1.15
) -> Image.Image:
    """
    Penyempurnaan gambar profesional (Tone, Vibrance, Clarity & Sharpness ala Corel PHOTO-PAINT).
    """
    # Auto-contrast dasar
    img = ImageOps.autocontrast(image, cutoff=1)

    # Kontras & Kecerahan
    if brightness != 1.0:
        enh_b = ImageEnhance.Brightness(img)
        img = enh_b.enhance(brightness)

    if contrast != 1.0:
        enh_c = ImageEnhance.Contrast(img)
        img = enh_c.enhance(contrast)

    # Warna / Vibrance
    if color != 1.0 and img.mode in ("RGB", "RGBA"):
        enh_col = ImageEnhance.Color(img)
        img = enh_col.enhance(color)

    # Ketajaman
    if sharpness != 1.0:
        enh_s = ImageEnhance.Sharpness(img)
        img = enh_s.enhance(sharpness)

    return img

def trace_bitmap_to_svg(image: Image.Image, max_colors: int = 4, detail_level: int = 3) -> str:
    """
    PowerTRACE Simulator: Mengonversi gambar/logo/tanda tangan bitmap menjadi kode SVG Vektor.
    """
    # Resize untuk performa responsif jika terlalu besar
    w, h = image.size
    max_dim = 600
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        w, h = int(w * scale), int(h * scale)
        image = image.resize((w, h), Image.Resampling.LANCZOS)

    # Posterize / Color quantization
    quantized = image.convert("RGB").quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette() or []
    color_hexes = []
    num_available = len(palette) // 3
    for i in range(max_colors):
        if i < num_available:
            r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
            color_hexes.append(f"#{r:02x}{g:02x}{b:02x}")
        else:
            color_hexes.append("#ffffff")

    np_grid = np.array(quantized)

    # Generate SVG rectangles/paths for clusters
    svg_elements = []
    step = max(1, 4 - detail_level)

    for y in range(0, h, step):
        current_color_idx = -1
        start_x = 0
        for x in range(0, w, step):
            idx = np_grid[min(y, h-1), min(x, w-1)]
            if idx != current_color_idx:
                if current_color_idx != -1:
                    # Gambar segmen sebelumnya
                    fill = color_hexes[current_color_idx]
                    svg_elements.append(
                        f'<rect x="{start_x}" y="{y}" width="{x - start_x}" height="{step}" fill="{fill}" />'
                    )
                current_color_idx = idx
                start_x = x
        # Gambar sisa segmen di akhir baris
        if current_color_idx != -1:
            fill = color_hexes[current_color_idx]
            svg_elements.append(
                f'<rect x="{start_x}" y="{y}" width="{w - start_x}" height="{step}" fill="{fill}" />'
            )

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <style>rect {{ shape-rendering: crispEdges; }}</style>
  </defs>
  <!-- PowerTRACE Vector Output -->
  {''.join(svg_elements)}
</svg>"""
    return svg_content
