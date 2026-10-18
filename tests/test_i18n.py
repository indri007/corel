"""Test P2-4: i18n."""
from utils.i18n import t

def test_t_id():
    assert t("upload", "id") == "Unggah Berkas"

def test_t_en():
    assert t("upload", "en") == "Upload File"

def test_t_fallback():
    assert t("nonexistent", "en") == "nonexistent"
