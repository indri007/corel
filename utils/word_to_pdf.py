import subprocess, tempfile, os, shutil

def word_to_pdf(src_path: str) -> str:
    """Konversi .doc / .docx / .odt / .rtf → PDF via LibreOffice headless (fidelity penuh)."""
    outdir = tempfile.mkdtemp(prefix="w2pdf_")
    try:
        result = subprocess.run(
            ["soffice", "--headless", "--norestore", "--convert-to", "pdf",
             "--outdir", outdir, src_path],
            capture_output=True, text=True, timeout=180
        )
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice gagal: {result.stderr.strip()}")
        base = os.path.splitext(os.path.basename(src_path))[0] + ".pdf"
        out = os.path.join(outdir, base)
        if not os.path.exists(out):
            raise RuntimeError(f"Output tidak ditemukan: {out}")
        return out
    finally:
        pass  # biarkan outdir, hapus manual setelah dipakai
