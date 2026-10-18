import io
import pymupdf
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from utils.stamp_generator import generate_vector_stamp_svg, svg_to_png_bytes

def render_pdf_page_to_image(pdf_bytes: bytes, page_num: int = 0, zoom: float = 2.0) -> Image.Image:
    """
    Merender halaman PDF menjadi gambar PIL resolusi tinggi (DPI tinggi) untuk pratinjau.
    """
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    if page_num >= len(doc):
        page_num = len(doc) - 1
    page = doc[page_num]
    mat = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_data = pix.tobytes("png")
    return Image.open(io.BytesIO(img_data))

def generate_qr_code_image(text: str, size: int = 120) -> bytes:
    """
    Menghasilkan gambar QR Code verifikasi dokumen dalam format PNG bytes.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=1,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def enhance_existing_pdf(
    pdf_bytes: bytes,
    header_title: str = "PT GLOBAL TEKNOLOGI INOVASI",
    header_subtitle: str = "Enterprise Architecture & Digital Transformation Division",
    watermark_text: str = "CONFIDENTIAL",
    footer_text: str = "Dokumen Resmi Terverifikasi Sistem Digital CorelDoc Pro",
    accent_color: str = "#00c853",
    apply_watermark: bool = True,
    apply_header: bool = True,
    apply_footer: bool = True,
    apply_border: bool = True,
    apply_stamp: bool = True,
    stamp_org: str = "PT GLOBAL TEKNOLOGI INOVASI",
    stamp_dept: str = "DEPARTEMEN LEGAL & AUDIT",
    stamp_status: str = "DISETUJUI & SAH",
    stamp_date: str = "18 OKT 2026"
) -> bytes:
    """
    Mentransformasi PDF yang sudah ada menjadi dokumen berstandar profesional ala CorelDRAW:
    - Menambahkan Header / Kop Surat Vektor
    - Menambahkan Footer & Nomor Halaman
    - Menambahkan Watermark Vektor Semi-Transparan
    - Menambahkan QR Code Validasi
    - Menambahkan Stempel Resmi Vektor (di halaman terakhir)
    - Menambahkan Border Aksen Ganda
    """
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)

    # Warna aksen (RGB float 0..1 untuk PyMuPDF)
    hex_clean = accent_color.lstrip("#")
    r = int(hex_clean[0:2], 16) / 255.0
    g = int(hex_clean[2:4], 16) / 255.0
    b = int(hex_clean[4:6], 16) / 255.0

    # Buat QR code verifikasi
    qr_bytes = generate_qr_code_image(f"VERIFIED:{header_title}|{stamp_date}")

    # Buat stempel PNG bytes jika stempel diaktifkan
    stamp_png = None
    if apply_stamp:
        stamp_svg = generate_vector_stamp_svg(
            org_name=stamp_org,
            dept_name=stamp_dept,
            status_text=stamp_status,
            date_str=stamp_date,
            color=accent_color
        )
        stamp_png = svg_to_png_bytes(stamp_svg, zoom=2)

    for page_idx, page in enumerate(doc):
        rect = page.rect
        w = rect.width
        h = rect.height

        # 1. Border Elegan (Double Accent Border)
        if apply_border:
            margin = 20
            # Garis tepi tipis luar
            page.draw_rect(pymupdf.Rect(margin, margin, w - margin, h - margin), color=(r, g, b), width=1.5)
            # Garis tepi aksen dalam
            page.draw_rect(pymupdf.Rect(margin + 4, margin + 4, w - margin - 4, h - margin - 4), color=(r, g, b), width=0.5)

        # 2. Watermark Vektor Diagonal
        if apply_watermark and watermark_text.strip():
            font_size = 48
            p_center = pymupdf.Point(w / 4, h / 2)
            rot_mat = pymupdf.Matrix(45)
            page.insert_text(
                p_center,
                watermark_text.upper(),
                fontsize=font_size,
                fontname="helv",
                color=(0.85, 0.85, 0.88),
                morph=(p_center, rot_mat)
            )

        # 3. Header / Kop Surat Profesional
        if apply_header and header_title.strip():
            # Aksen bar bagian atas
            page.draw_rect(pymupdf.Rect(25, 25, w - 25, 30), color=(r, g, b), fill=(r, g, b))
            # Judul Instansi
            page.insert_text(
                pymupdf.Point(35, 48),
                header_title.upper(),
                fontsize=11,
                fontname="helv",
                color=(0.1, 0.15, 0.25)
            )
            # Subtitle
            if header_subtitle.strip():
                page.insert_text(
                    pymupdf.Point(35, 60),
                    header_subtitle,
                    fontsize=8,
                    fontname="helv",
                    color=(0.4, 0.45, 0.55)
                )
            # Garis pemisah ganda
            page.draw_line(pymupdf.Point(35, 66), pymupdf.Point(w - 35, 66), color=(r, g, b), width=1.2)
            page.draw_line(pymupdf.Point(35, 68), pymupdf.Point(w - 35, 68), color=(0.7, 0.7, 0.7), width=0.5)

        # 4. Footer & Nomor Halaman
        if apply_footer:
            footer_y = h - 35
            # Garis pemisah footer
            page.draw_line(pymupdf.Point(35, footer_y - 10), pymupdf.Point(w - 35, footer_y - 10), color=(0.8, 0.8, 0.8), width=0.8)

            # Teks disclaimer / legal
            page.insert_text(
                pymupdf.Point(35, footer_y + 4),
                footer_text,
                fontsize=7.5,
                fontname="helv",
                color=(0.4, 0.45, 0.5)
            )

            # Nomor Halaman "Halaman X dari Y"
            page_str = f"Halaman {page_idx + 1} dari {total_pages}"
            page.insert_text(
                pymupdf.Point(w - 120, footer_y + 4),
                page_str,
                fontsize=8,
                fontname="helv",
                color=(0.2, 0.25, 0.35)
            )

            # QR Code Verifikasi di pojok kiri bawah
            qr_rect = pymupdf.Rect(w - 65, footer_y - 35, w - 35, footer_y - 5)
            page.insert_image(qr_rect, stream=qr_bytes)

        # 5. Stempel Resmi di Halaman Terakhir
        if apply_stamp and stamp_png and page_idx == (total_pages - 1):
            stamp_w, stamp_h = 110, 110
            stamp_rect = pymupdf.Rect(w - 160, h - 170, w - 160 + stamp_w, h - 170 + stamp_h)
            page.insert_image(stamp_rect, stream=stamp_png)

    output_buf = io.BytesIO()
    doc.save(output_buf)
    return output_buf.getvalue()

def create_professional_document_from_text(
    title: str,
    content: str,
    company_name: str = "PT GLOBAL TEKNOLOGI INOVASI",
    doc_number: str = "REF: 2026/GTI-DIR/DOC-049",
    accent_color_hex: str = "#00c853"
) -> bytes:
    """
    Menyusun dokumen baru dari teks mentah dengan tipografi profesional tingkat eksekutif.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=80,
        bottomMargin=65
    )

    styles = getSampleStyleSheet()

    # Style Judul
    title_style = ParagraphStyle(
        'ExecutiveTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=12
    )

    # Style Metadata Dokumen
    meta_style = ParagraphStyle(
        'ExecutiveMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=18
    )

    # Style Paragraf Isi
    body_style = ParagraphStyle(
        'ExecutiveBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        alignment=4, # Justified
        spaceAfter=12
    )

    story = []
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"Nomor Dokumen: <b>{doc_number}</b> | Penerbit: <b>{company_name}</b>", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor(accent_color_hex), spaceAfter=18))

    # Split konten per paragraf
    paragraphs = content.split("\n\n")
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.replace("\n", " "), body_style))
            story.append(Spacer(1, 4))

    doc.build(story)
    raw_pdf = buffer.getvalue()

    # Enhance dengan header, footer, border & watermark resmi
    return enhance_existing_pdf(
        raw_pdf,
        header_title=company_name,
        header_subtitle=f"Official Publication - {doc_number}",
        accent_color=accent_color_hex
    )
