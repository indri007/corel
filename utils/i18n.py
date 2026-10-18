"""Terjemahan sederhana Indonesia/English via session_state."""
from __future__ import annotations

TRANSLATIONS: dict[str, dict[str, str]] = {
    "id": {
        "title": "CorelDoc Studio",
        "upload": "Unggah Berkas",
        "process": "Proses",
        "download": "Unduh",
        "language": "Bahasa",
        "theme": "Tema",
        "light": "Terang",
        "dark": "Gelap",
    },
    "en": {
        "title": "CorelDoc Studio",
        "upload": "Upload File",
        "process": "Process",
        "download": "Download",
        "language": "Language",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
    },
}


def t(key: str, lang: str = "id") -> str:
    """Terjemahkan key ke bahasa lang, fallback ke Indonesia."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["id"]).get(key, key)
