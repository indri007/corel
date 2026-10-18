"""QR verifikasi berisi URL + hash SHA-256 dokumen untuk audit."""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

import qrcode

logger = logging.getLogger(__name__)


def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    """Hitung SHA-256 file secara streaming."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def build_verify_url(base_url: str, doc_hash: str, doc_id: str) -> str:
    """Bangun URL verifikasi yang bisa dibuka di browser."""
    base = base_url.rstrip("/")
    return f"{base}/verify/{doc_id}?hash={doc_hash}"


def make_qr(url: str, out_png: str | Path, box_size: int = 8) -> Path:
    """Buat QR PNG dari URL."""
    img = qrcode.make(url, box_size=box_size)
    out = Path(out_png)
    img.save(out)
    logger.info("QR dibuat: %s → %s", url, out)
    return out


def make_manifest(doc_path: str | Path, doc_id: str, base_url: str) -> dict:
    """Buat manifest audit: id, hash, url, timestamp."""
    import datetime
    h = sha256_file(doc_path)
    now = datetime.datetime.now(datetime.timezone.utc)
    return {
        "id": doc_id,
        "filename": Path(doc_path).name,
        "sha256": h,
        "url": build_verify_url(base_url, h, doc_id),
        "created": now.isoformat(),
    }


def write_manifest(manifest: dict, out_json: str | Path) -> Path:
    """Tulis manifest ke file JSON."""
    p = Path(out_json)
    p.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return p
