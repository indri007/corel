import math
import io
from PIL import Image
import pymupdf

def generate_vector_stamp_svg(
    org_name="KEMENTERIAN RISET & TEKNOLOGI",
    dept_name="DIREKTORAT JENDERAL INOVASI",
    status_text="DISETUJUI & SAH",
    date_str="18 OKT 2026",
    color="#0d47a1",
    diameter=320
):
    """
    Menghasilkan stempel resmi melingkar format vektor SVG (ala CorelDRAW).
    """
    cx, cy = diameter / 2, diameter / 2
    r_outer = diameter / 2 - 8
    r_inner1 = r_outer - 6
    r_inner2 = r_inner1 - 32
    r_center = r_inner2 - 6

    # Unique IDs for SVG textPaths
    upper_path_id = "upper_arc"
    lower_path_id = "lower_arc"

    r_text_upper = (r_inner1 + r_inner2) / 2
    r_text_lower = (r_inner1 + r_inner2) / 2

    # SVG Path arcs
    # Upper arc: from (-r, 0) to (r, 0) going through top
    upper_d = f"M {cx - r_text_upper},{cy} A {r_text_upper},{r_text_upper} 0 0,1 {cx + r_text_upper},{cy}"
    # Lower arc: from (-r, 0) to (r, 0) going through bottom
    lower_d = f"M {cx - r_text_lower},{cy} A {r_text_lower},{r_text_lower} 0 0,0 {cx + r_text_lower},{cy}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {diameter} {diameter}" width="{diameter}" height="{diameter}">
  <defs>
    <path id="{upper_path_id}" d="{upper_d}" fill="none" />
    <path id="{lower_path_id}" d="{lower_d}" fill="none" />
  </defs>

  <!-- Outer Double Rings -->
  <circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="{color}" stroke-width="4.5" />
  <circle cx="{cx}" cy="{cy}" r="{r_inner1}" fill="none" stroke="{color}" stroke-width="1.8" />
  <circle cx="{cx}" cy="{cy}" r="{r_inner2}" fill="none" stroke="{color}" stroke-width="1.8" />
  <circle cx="{cx}" cy="{cy}" r="{r_center}" fill="none" stroke="{color}" stroke-width="2.5" />

  <!-- Upper Text (Curved) -->
  <text font-family="'Arial', 'Helvetica', sans-serif" font-weight="900" font-size="15" fill="{color}" letter-spacing="2">
    <textPath href="#{upper_path_id}" startOffset="50%" text-anchor="middle">
      {org_name.upper()}
    </textPath>
  </text>

  <!-- Lower Text (Curved) -->
  <text font-family="'Arial', 'Helvetica', sans-serif" font-weight="800" font-size="13" fill="{color}" letter-spacing="1.5">
    <textPath href="#{lower_path_id}" startOffset="50%" text-anchor="middle">
      {dept_name.upper()}
    </textPath>
  </text>

  <!-- Divider Stars -->
  <text x="{cx - r_text_upper + 6}" y="{cy + 5}" font-size="18" fill="{color}" text-anchor="middle">★</text>
  <text x="{cx + r_text_upper - 6}" y="{cy + 5}" font-size="18" fill="{color}" text-anchor="middle">★</text>

  <!-- Center Status Box -->
  <rect x="{cx - 85}" y="{cy - 24}" width="170" height="48" rx="4" fill="none" stroke="{color}" stroke-width="2" />
  <text x="{cx}" y="{cy - 3}" font-family="'Arial Black', sans-serif" font-weight="900" font-size="15" fill="{color}" text-anchor="middle" letter-spacing="1">
    {status_text.upper()}
  </text>
  <text x="{cx}" y="{cy + 16}" font-family="'Courier New', monospace" font-weight="700" font-size="12" fill="{color}" text-anchor="middle">
    {date_str}
  </text>
</svg>"""
    return svg

def svg_to_png_bytes(svg_code, zoom=2):
    """
    Mengonversi kode SVG ke PNG bytes dengan resolusi tinggi menggunakan PyMuPDF.
    """
    doc = pymupdf.open(stream=svg_code.encode("utf-8"), filetype="svg")
    page = doc[0]
    mat = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=True)
    return pix.tobytes("png")
