"""Tanda tangan digital PDF (PAdES) via pyhanko."""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_self_signed_cert(
    cert_path: str | Path,
    key_path: str | Path,
    common_name: str = "CorelDoc Studio",
) -> tuple[Path, Path]:
    """Buat sertifikat self-signed + private key untuk testing.

    Args:
        cert_path: Path output sertifikat (.pem).
        key_path: Path output private key (.pem).
        common_name: CN sertifikat.

    Returns:
        Tuple (cert_path, key_path).
    """
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    import datetime

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365))
        .sign(key, hashes.SHA256())
    )

    cp, kp = Path(cert_path), Path(key_path)
    cp.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    kp.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    logger.info("Sertifikat self-signed dibuat: %s", cp)
    return cp, kp


def sign_pdf(
    src_pdf: str | Path,
    out_pdf: str | Path,
    key_path: str | Path,
    cert_path: str | Path,
    field_name: str = "Signature1",
    reason: str = "Disetujui secara digital",
    location: str = "Indonesia",
) -> Path:
    """Tanda tangani PDF dengan PAdES (pyhanko).

    Args:
        src_pdf: PDF sumber.
        out_pdf: PDF output bertanda tangan.
        key_path: Private key PEM.
        cert_path: Sertifikat PEM.
        field_name: Nama field signature.
        reason: Alasan penandatanganan.
        location: Lokasi penandatanganan.

    Returns:
        Path PDF output.
    """
    from pyhanko.sign import signers
    from pyhanko.sign.fields import SigFieldSpec
    from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter

    src, out = Path(src_pdf), Path(out_pdf)
    if not src.exists():
        raise FileNotFoundError(f"PDF tidak ditemukan: {src}")

    signer = signers.SimpleSigner.load(
        key_file=str(key_path),
        cert_file=str(cert_path),
    )
    if signer is None:
        raise RuntimeError("Gagal memuat signer. Periksa key/cert.")

    with src.open("rb") as inf:
        w = IncrementalPdfFileWriter(inf)
        meta = signers.PdfSignatureMetadata(
            field_name=field_name, reason=reason, location=location,
        )
        with out.open("wb") as outf:
            signers.sign_pdf(
                w, meta,
                signer=signer,
                output=outf,
                new_field_spec=SigFieldSpec(sig_field_name=field_name),
            )
    logger.info("PDF ditandatangani → %s", out)
    return out


def verify_signature(pdf_path: str | Path) -> dict:
    """Verifikasi tanda tangan PDF. Return dict ringkas."""
    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign.validation import validate_pdf_signature

    p = Path(pdf_path)
    with p.open("rb") as f:
        reader = PdfFileReader(f, strict=False)
        results = []
        for sig in reader.embedded_signatures:
            try:
                status = validate_pdf_signature(sig, signer_validation_context=None)
                results.append({
                    "field": sig.field_name,
                    "valid": status.valid,
                    "intact": status.intact,
                    "trusted": status.trusted,
                    "signer": str(status.signing_cert.subject) if status.signing_cert else None,
                })
            except Exception as e:
                results.append({"field": sig.field_name, "error": str(e)})
    return {"count": len(results), "signatures": results}
