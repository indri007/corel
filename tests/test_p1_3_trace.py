"""Test P1-3: tracing produksi."""
from pathlib import Path
import subprocess
import pytest
from PIL import Image, ImageDraw


@pytest.fixture
def sample_png(tmp_path: Path) -> Path:
    img = Image.new("RGB", (400, 400), "white")
    d = ImageDraw.Draw(img)
    d.ellipse([100, 100, 300, 300], fill="black")
    p = tmp_path / "circle.png"
    img.save(p)
    return p


def test_remove_background(sample_png):
    from utils.trace_advanced import remove_background
    out = remove_background(sample_png, threshold=240)
    assert out.exists()
    assert Image.open(out).mode == "RGBA"


def test_vtracer_produces_svg(sample_png, tmp_path):
    from utils.trace_advanced import trace_color_vtracer
    out = tmp_path / "out.svg"
    trace_color_vtracer(sample_png, out, n_colors=4)
    assert out.exists() and out.stat().st_size > 0
    assert "<svg" in out.read_text(errors="ignore").lower()


def test_potrace_centerline(sample_png, tmp_path):
    if subprocess.run(["which", "potrace"], capture_output=True).returncode != 0:
        pytest.skip("potrace tidak terpasang")
    from utils.trace_advanced import trace_centerline_potrace
    out = tmp_path / "line.svg"
    trace_centerline_potrace(sample_png, out)
    assert out.exists() and "<svg" in out.read_text(errors="ignore").lower()


def test_batch_trace(sample_png, tmp_path):
    from utils.trace_advanced import batch_trace
    outs = batch_trace([sample_png, sample_png], tmp_path / "batch", do_svgo=False)
    assert len(outs) == 2
