"""Test P3-3: AI SVG (offline — hanya extract & save)."""
from pathlib import Path
import pytest
import utils.ai_svg as aisvg


def test_extract_svg_basic():
    raw = "Here is your SVG:\n<svg xmlns='http://www.w3.org/2000/svg'><circle r='5'/></svg>\ndone."
    svg = aisvg.extract_svg(raw)
    assert svg.startswith("<svg") and svg.endswith("</svg>")


def test_extract_no_svg():
    with pytest.raises(ValueError):
        aisvg.extract_svg("no svg here")


def test_save_invalid_svg(tmp_path):
    with pytest.raises(ValueError):
        aisvg.save_svg_text("<svg><unclosed>", tmp_path / "x.svg")


def test_save_valid_svg(tmp_path):
    p = aisvg.save_svg_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>", tmp_path / "ok.svg")
    assert p.exists()


def test_hf_token_missing(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="HF_TOKEN"):
        aisvg.text_to_svg_hf("test")
