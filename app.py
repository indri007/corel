import io
import streamlit as st
from PIL import Image
import pymupdf

# Konversi DOCX → PDF
try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# Import modul utils
from utils.stamp_generator import generate_vector_stamp_svg, svg_to_png_bytes
from utils.image_enhancer import clean_scanned_document, enhance_photo_professional, trace_bitmap_to_svg
from utils.pdf_processor import (
    render_pdf_page_to_image,
    enhance_existing_pdf,
    create_professional_document_from_text
)

# -----------------------------------------------------------------------------
# Konfigurasi Halaman Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CorelDoc Studio | Professional Document & Vector Suite",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom CSS Styling (Rich Aesthetic ala CorelDRAW & Modern Dark Glassmorphism)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Gradient Header & Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, rgba(0, 200, 83, 0.15) 0%, rgba(13, 71, 161, 0.2) 100%);
        border: 1px solid rgba(0, 200, 83, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }

    .badge-pill {
        display: inline-block;
        background: rgba(0, 200, 83, 0.2);
        color: #00e676;
        border: 1px solid rgba(0, 200, 83, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 8px;
    }

    .badge-accent {
        display: inline-block;
        background: rgba(41, 121, 255, 0.2);
        color: #82b1ff;
        border: 1px solid rgba(41, 121, 255, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }

    .feature-card {
        background: #182032;
        border: 1px solid #23304a;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .feature-card:hover {
        border-color: #00c853;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Header Utama
# -----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
        <div>
            <div style="margin-bottom: 8px;">
                <span class="badge-pill">CORELDRAW-INSPIRED</span>
                <span class="badge-accent">STREAMLIT CLOUD EDITION</span>
            </div>
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
                🎨 CorelDoc Studio <span style="color: #00e676; font-size: 1.8rem;">Pro</span>
            </h1>
            <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 1rem;">
                Transformasi tulisan, dokumen, PDF, dan gambar menjadi format korporat profesional dengan presisi vektor.
            </p>
        </div>
        <div>
            <a href="https://github.com/indri007/corel" target="_blank" style="text-decoration: none;">
                <button style="background: #1e293b; color: #e2e8f0; border: 1px solid #334155; padding: 10px 18px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                    ⭐ GitHub: indri007/corel
                </button>
            </a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Navigasi Tab
# -----------------------------------------------------------------------------
tab_pdf, tab_img, tab_trace, tab_stamp, tab_catalog = st.tabs([
    "📄 Penyempurna PDF & Tulisan",
    "🖼️ Pembersih Scan & Gambar",
    "⚡ PowerTRACE (Bitmap → Vektor)",
    "🏵️ Pembuat Stempel Resmi",
    "📚 Katalog Ekosistem Corel"
])

# =============================================================================
# TAB 1: PENYEMPURNA PDF & TULISAN
# =============================================================================
with tab_pdf:
    st.subheader("Transformasi Dokumen & PDF ke Standar Korporat")
    st.caption("Menambahkan Kop Surat vektor, garis pemisah ganda, stempel resmi, watermark, nomor halaman, dan QR code validasi.")

    col_input, col_preview = st.columns([1, 1.2])

    with col_input:
        input_type = st.radio(
            "Pilih Sumber Dokumen:",
            ["Unggah Berkas PDF", "Tulis / Tempel Teks Baru"],
            horizontal=True
        )

        uploaded_pdf = None
        doc_title = ""
        doc_content = ""

        if input_type == "Unggah Berkas PDF":
            uploaded_pdf = st.file_uploader(
                "Pilih Berkas PDF atau DOCX (Word):",
                type=["pdf", "docx", "doc"],
                key="pdf_uploader",
                help="Mendukung file PDF dan Word (.docx). File Word akan dikonversi otomatis ke PDF."
            )
        else:
            doc_title = st.text_input("Judul Dokumen:", value="SURAT KEPUTUSAN DIREKSI TENTANG STANDARISASI DOKUMEN")
            doc_number = st.text_input("Nomor Registrasi / Surat:", value="SK/DIR-GTI/X/2026-088")
            doc_content = st.text_area(
                "Isi Paragraf Dokumen:",
                value="""Dengan ini diberitahukan kepada seluruh divisi bahwa terhitung mulai tanggal 18 Oktober 2026, seluruh dokumen operasional, desain teknik, dan berkas perjanjian wajib menggunakan standar format tata letak CorelDoc Pro.

Standarisasi ini mencakup penyertaan kop surat resmi dengan aksen ganda vektor, stempel otentikasi digital yang dapat diverifikasi melalui QR Code, serta penomoran halaman otomatis guna memastikan keaslian dan integritas berkas.

Setiap departemen diharapkan menyesuaikan tata kelola dokumen sesuai dengan pedoman teknis yang telah ditentukan dalam keputusan ini.""",
                height=180
            )

        st.markdown("---")
        st.markdown("#### ⚙️ Pengaturan Desain & Ornamen")

        c1, c2 = st.columns(2)
        with c1:
            header_name = st.text_input("Nama Instansi / Perusahaan:", value="PT GLOBAL TEKNOLOGI INOVASI")
            accent_col = st.color_picker("Warna Aksen Korporat:", value="#00c853")
            watermark_val = st.text_input("Teks Watermark:", value="CONFIDENTIAL")
        with c2:
            header_sub = st.text_input("Sub-Judul / Divisi:", value="Directorate of Technology & Engineering Systems")
            footer_val = st.text_input("Teks Footer / Legal Disclaimer:", value="Dokumen Resmi Terverifikasi - Rahasia & Hak Cipta Terlindungi")

        st.markdown("##### Fitur Ornamen Vektor:")
        f1, f2, f3, f4, f5 = st.columns(5)
        with f1:
            en_header = st.checkbox("Kop Surat", value=True)
        with f2:
            en_footer = st.checkbox("Footer & Hal", value=True)
        with f3:
            en_border = st.checkbox("Border Ganda", value=True)
        with f4:
            en_watermark = st.checkbox("Watermark", value=True)
        with f5:
            en_stamp = st.checkbox("Stempel Resmi", value=True)

    with col_preview:
        st.markdown("#### 👁️ Pratinjau Dokumen Profesional")

        result_pdf_bytes = None

        if input_type == "Unggah Berkas PDF" and uploaded_pdf is not None:
            raw_bytes = uploaded_pdf.read()
            file_name_lower = uploaded_pdf.name.lower()

            # ── Konversi DOCX → PDF jika diperlukan ──
            if file_name_lower.endswith((".docx", ".doc")):
                if not HAS_DOCX:
                    st.error("Library `python-docx` belum terinstal. Jalankan: `pip install python-docx`")
                    st.stop()
                with st.spinner("Mengonversi file Word (.docx) ke PDF..."):
                    try:
                        docx_doc = DocxDocument(io.BytesIO(raw_bytes))
                        full_text = "\n\n".join(
                            para.text for para in docx_doc.paragraphs if para.text.strip()
                        )
                        if not full_text.strip():
                            st.warning("Dokumen Word kosong atau hanya berisi gambar. Teks tidak ditemukan.")
                            full_text = "(Dokumen Word tidak mengandung teks yang dapat diekstrak.)"

                        # Gunakan pipeline pembuatan dokumen profesional dari teks
                        raw_bytes = create_professional_document_from_text(
                            title=doc_title if doc_title else uploaded_pdf.name.rsplit(".", 1)[0],
                            content=full_text,
                            company_name=header_name,
                            doc_number="DOCX-CONVERT",
                            accent_color_hex=accent_col
                        )
                        st.success(f"✅ File Word berhasil dikonversi! ({len(full_text):,} karakter diekstrak)")
                    except Exception as e:
                        st.error(f"Gagal mengonversi DOCX: {e}")
                        st.stop()

            with st.spinner("Memproses transformasi dokumen..."):
                result_pdf_bytes = enhance_existing_pdf(
                    raw_bytes,
                    header_title=header_name,
                    header_subtitle=header_sub,
                    watermark_text=watermark_val,
                    footer_text=footer_val,
                    accent_color=accent_col,
                    apply_watermark=en_watermark,
                    apply_header=en_header,
                    apply_footer=en_footer,
                    apply_border=en_border,
                    apply_stamp=en_stamp
                )
        elif input_type != "Unggah Berkas PDF" and doc_content.strip():
            with st.spinner("Menyusun dokumen profesional dari teks..."):
                result_pdf_bytes = create_professional_document_from_text(
                    title=doc_title,
                    content=doc_content,
                    company_name=header_name,
                    doc_number=doc_number,
                    accent_color_hex=accent_col
                )

        if result_pdf_bytes:
            preview_img = render_pdf_page_to_image(result_pdf_bytes, page_num=0, zoom=2.0)
            st.image(preview_img, caption="Pratinjau Hasil Dokumen Siap Cetak (Halaman 1)", use_container_width=True)

            st.download_button(
                label="📥 Unduh PDF Profesional (300 DPI)",
                data=result_pdf_bytes,
                file_name="Dokumen_Profesional_CorelDoc.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.info("💡 Silakan unggah PDF atau tuliskan teks dokumen pada panel di samping untuk melihat hasil transformasi profesional.")

# =============================================================================
# TAB 2: PEMBERSIH SCAN & GAMBAR
# =============================================================================
with tab_img:
    st.subheader("Penyempurnaan Gambar & Pembersihan Scan Dokumen")
    st.caption("Memutihkan latar belakang kertas yang buram/kotor, menajamkan teks tulisan, serta mengoptimalkan kontras & vibrance gambar.")

    col_img_in, col_img_out = st.columns([1, 1.2])

    with col_img_in:
        uploaded_img = st.file_uploader(
            "Unggah Gambar / Dokumen Scan (PNG, JPG, WebP):",
            type=["png", "jpg", "jpeg", "webp"],
            key="img_enhancer_uploader"
        )

        mode_process = st.selectbox(
            "Pilih Mode Pemrosesan:",
            ["Pembersih Scan Dokumen (White Background & Sharp Text)", "Penyempurna Foto & Ilustrasi (Tone, Vibrance, Sharpness)"]
        )

        if mode_process.startswith("Pembersih"):
            aggressiveness = st.slider("Tingkat Agresivitas Pemutihan Kertas:", 0.5, 2.0, 1.2, 0.1)
        else:
            b_val = st.slider("Brightness:", 0.5, 2.0, 1.05, 0.05)
            c_val = st.slider("Contrast:", 0.5, 2.0, 1.2, 0.05)
            s_val = st.slider("Sharpness:", 0.5, 3.0, 1.5, 0.1)
            col_val = st.slider("Color Vibrance:", 0.0, 2.0, 1.15, 0.05)

    with col_img_out:
        if uploaded_img is not None:
            raw_img = Image.open(uploaded_img)

            if mode_process.startswith("Pembersih"):
                processed_img = clean_scanned_document(raw_img, aggressiveness=aggressiveness)
            else:
                processed_img = enhance_photo_professional(raw_img, brightness=b_val, contrast=c_val, sharpness=s_val, color=col_val)

            c_orig, c_proc = st.columns(2)
            with c_orig:
                st.markdown("**Sebelum (Original):**")
                st.image(raw_img, use_container_width=True)
            with c_proc:
                st.markdown("**Sesudah (Profesional):**")
                st.image(processed_img, use_container_width=True)

            out_buf = io.BytesIO()
            processed_img.save(out_buf, format="PNG")
            st.download_button(
                label="📥 Unduh Gambar Berkualitas Tinggi (PNG)",
                data=out_buf.getvalue(),
                file_name="gambar_profesional.png",
                mime="image/png",
                use_container_width=True
            )

            # Fitur Ekstraksi Tulisan OCR Tesseract
            st.markdown("---")
            st.markdown("##### 🔍 Ekstraksi Tulisan (OCR Tesseract)")
            if st.button("Jalankan Pembacaan Teks (OCR)", key="btn_ocr"):
                with st.spinner("Membaca teks dari gambar scan menggunakan Tesseract..."):
                    try:
                        import pytesseract
                        extracted_text = pytesseract.image_to_string(processed_img)
                        if extracted_text.strip():
                            st.text_area("Hasil Ekstraksi Teks (Dapat Diedit/Disalin):", value=extracted_text, height=140)
                            st.success("Teks berhasil diekstrak! Anda dapat menyalin teks ini ke Tab 1 (Penyempurna PDF) untuk diformat ulang.")
                        else:
                            st.warning("Tidak ditemukan teks yang dapat dibaca secara jelas pada gambar ini.")
                    except Exception as e:
                        st.error(f"Gagal memproses OCR: {str(e)}")
        else:
            st.info("💡 Unggah gambar tanda tangan, diagram, scan kertas, atau foto untuk melakukan pembersihan & penajaman otomatis.")

# =============================================================================
# TAB 3: POWERTRACE (BITMAP TO VECTOR SVG)
# =============================================================================
with tab_trace:
    st.subheader("⚡ PowerTRACE: Vektorisasi Bitmap ke SVG Murni")
    st.caption("Mengonversi logo, gambar, tanda tangan, atau sketsa bitmap menjadi garis vektor SVG yang dapat diperbesar tanpa pecah.")

    col_trace_in, col_trace_out = st.columns([1, 1.2])

    with col_trace_in:
        trace_file = st.file_uploader(
            "Unggah Logo / Gambar untuk Di-vektorisasi:",
            type=["png", "jpg", "jpeg", "webp"],
            key="trace_uploader"
        )
        max_col = st.slider("Jumlah Palet Warna Vektor:", 2, 8, 4)
        detail_lvl = st.slider("Tingkat Detail Vektor:", 1, 3, 2)

    with col_trace_out:
        if trace_file is not None:
            t_img = Image.open(trace_file)
            with st.spinner("Memproses konversi ke format vektor SVG..."):
                svg_result = trace_bitmap_to_svg(t_img, max_colors=max_col, detail_level=detail_lvl)

            st.markdown("#### Hasil Vektor SVG:")
            st.html(
                f'<div style="background: #ffffff; padding: 16px; border-radius: 8px; text-align: center;">{svg_result}</div>'
            )

            st.download_button(
                label="📥 Unduh Berkas Vektor SVG (.svg)",
                data=svg_result.encode("utf-8"),
                file_name="vektor_powertrace.svg",
                mime="image/svg+xml",
                use_container_width=True
            )
        else:
            st.info("💡 Unggah gambar bertipe raster (PNG/JPG) untuk membuat output vektor SVG ala CorelDRAW PowerTRACE.")

# =============================================================================
# TAB 4: PEMBUAT STEMPEL RESMI
# =============================================================================
with tab_stamp:
    st.subheader("🏵️ Pembuat Stempel Resmi Vektor (Official Circular Stamp)")
    st.caption("Menghasilkan stempel legal melingkar resolusi tinggi untuk otentikasi dokumen dinas atau korporat.")

    col_st_cfg, col_st_view = st.columns([1, 1.2])

    with col_st_cfg:
        s_org = st.text_input("Teks Melingkar Atas (Nama Organisasi):", value="KEMENTERIAN RISET & TEKNOLOGI")
        s_dept = st.text_input("Teks Melingkar Bawah (Unit Kerja):", value="DIREKTORAT JENDERAL INOVASI")
        s_status = st.text_input("Teks Kotak Tengah (Status Dokumen):", value="DISETUJUI & SAH")
        s_date = st.text_input("Tanggal Verifikasi:", value="18 OKT 2026")
        s_color = st.selectbox(
            "Warna Tinta Stempel:",
            ["#0d47a1 (Biru Dinas)", "#b71c1c (Merah Resmi)", "#00695c (Hijau Korporat)", "#4a148c (Ungu Royal)"]
        )
        chosen_hex = s_color.split(" ")[0]

    with col_st_view:
        stamp_svg = generate_vector_stamp_svg(
            org_name=s_org,
            dept_name=s_dept,
            status_text=s_status,
            date_str=s_date,
            color=chosen_hex,
            diameter=320
        )

        st.html(
            f'<div style="display: flex; justify-content: center; align-items: center; padding: 20px; background: #ffffff; border-radius: 12px;">{stamp_svg}</div>'
        )

        c_d1, c_d2 = st.columns(2)
        with c_d1:
            st.download_button(
                label="📥 Unduh SVG Vektor",
                data=stamp_svg.encode("utf-8"),
                file_name="stempel_resmi.svg",
                mime="image/svg+xml",
                use_container_width=True
            )
        with c_d2:
            stamp_png_bytes = svg_to_png_bytes(stamp_svg, zoom=3)
            st.download_button(
                label="📥 Unduh PNG Transparan",
                data=stamp_png_bytes,
                file_name="stempel_resmi.png",
                mime="image/png",
                use_container_width=True
            )

# =============================================================================
# TAB 5: KATALOG EKOSISTEM COREL & ALTERNATIF
# =============================================================================
with tab_catalog:
    st.subheader("📚 Ekosistem CorelDRAW & Alternatif Open-Source")
    st.caption("Repositori ini telah meng-clone dan mendokumentasikan alat-alat desain vektor terbaik dunia:")

    st.markdown("""
| Kategori | Alat / Proyek | Stack Teknologi | Peran & Kemampuan |
|---|---|---|---|
| **Klon CorelDRAW Native** | **TraceDraw** | Rust | Editor vektor *clean-room* yang mampu membaca dan menulis format berkas `.cdr`. |
| **Klon Desktop Pro** | **sK1** | Python, C | Editor ilustrasi open-source dengan dukungan warna CMYK dan parser `.cdr`. |
| **Klon Desktop Pro** | **Inkscape** | C++, GTK | Standar industri editor vektor berbasis SVG untuk ilustrasi & desain presisi. |
| **PWA Web Editor** | **Graphite** | Rust, WebAssembly | Editor 2D prosedural berbasis node yang berjalan di browser. |
| **Web SVG Editor** | **SVG-Edit & Method Draw** | JavaScript | Editor SVG cepat di browser tanpa instalasi. |
| **WebGPU Editor** | **Vectora** | JS, WGSL, WebGPU | Editor vektor masa depan berbasis WebGPU tanpa instalasi paket. |
| **UI/UX Platform** | **Penpot** | Clojure, TypeScript | Platform desain antarmuka open-source berbasis web dengan standar SVG. |
| **AI Foundation** | **SVGThinker-7B** | LLM | Model penalaran kecerdasan buatan khusus untuk menghasilkan kode SVG kompleks. |
| **AI Foundation** | **StarVector-8B** | AI Model | Mengubah gambar raster ke instruksi vektor SVG presisi tinggi. |
| **Render Engine** | **ThorVG** | C++, WebGPU | Mesin gambar vektor berkinerja tinggi untuk SVG dan animasi Lottie. |
| **Konverter Vektor** | **VTracer** | Rust | Konversi raster ke vektor SVG full-color dengan kecepatan tinggi. |
    """)

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 12px 0;">
    <b>CorelDoc Studio Pro</b> &bull; Dibangun untuk Kompatibilitas Streamlit Cloud & GitHub Deployment &bull; 
    Repositori: <a href="https://github.com/indri007/corel" target="_blank" style="color: #00e676; text-decoration: none;">github.com/indri007/corel</a>
</div>
""", unsafe_allow_html=True)
