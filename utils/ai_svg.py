"""Integrasi model HF untuk text-to-SVG / image-to-SVG.

Mendukung dua jalur:
1. Hugging Face Inference API (butuh HF_TOKEN) — ringan, tanpa GPU lokal.
2. Transformers pipeline lokal (butuh GPU/CPU besar) — opsional.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

HF_ROUTER = "https://router.huggingface.co/hf-inference/models"


def _token() -> str:
    """Ambil token Hugging Face dari st.secrets atau environment variable."""
    try:
        import streamlit as st
        if "HF_TOKEN" in st.secrets:
            return str(st.secrets["HF_TOKEN"]).strip()
    except Exception:
        pass
    return os.environ.get("HF_TOKEN", "").strip()


def text_to_svg_hf(prompt: str, model: str = "Caffin/SVGThinker-7B") -> str:
    """Generasi SVG dari prompt teks via HF Inference API."""
    tok = _token()
    if not tok:
        raise RuntimeError(
            "HF_TOKEN belum di-set. Dapatkan di https://huggingface.co/settings/tokens\n"
            "Lalu jalankan: export HF_TOKEN=hf_xxx"
        )
    url = f"{HF_ROUTER}/{model}"
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
        json={"inputs": prompt, "parameters": {"max_new_tokens": 2048}},
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f"HF error {r.status_code}: {r.text[:300]}")
    data = r.json()
    if isinstance(data, list) and data:
        return data[0].get("generated_text", "")
    return data.get("generated_text", "")


def extract_svg(text: str) -> str:
    """Ambil blok <svg>...</svg> dari output model yang mungkin berisi prosa."""
    import re
    m = re.search(r"<svg[\s\S]*?</svg>", text, re.IGNORECASE)
    if not m:
        raise ValueError("Tidak ada tag <svg> dalam output model.")
    return m.group(0)


def save_svg_text(svg_text: str, out: str | Path) -> Path:
    """Validasi minimal + simpan SVG."""
    from xml.etree import ElementTree as ET
    try:
        ET.fromstring(svg_text)
    except ET.ParseError as e:
        raise ValueError(f"SVG tidak valid: {e}") from e
    p = Path(out)
    p.write_text(svg_text, encoding="utf-8")
    return p


def local_text_to_svg(prompt: str, model_id: str = "Caffin/SVGThinker-7B") -> str:
    """Jalur lokal via transformers (butuh GPU/CPU besar). Opsional."""
    try:
        from transformers import pipeline
    except ImportError as e:
        raise RuntimeError("pip install transformers torch accelerate") from e
    pipe = pipeline("text-generation", model=model_id, device_map="auto")
    result = pipe(prompt, max_new_tokens=2048, do_sample=False)
    return result[0]["generated_text"]
