"""Test P3-2: editor SVG."""
from pathlib import Path
import pytest
import utils.svg_editor as sve


@pytest.fixture
def sample_svg(tmp_path: Path) -> Path:
    content = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
    <path id="p1" d="M10,10 L100,10 L100,100 Z" fill="#FF0000"/>
    <path id="p2" d="M20,20 L80,20 L80,80 Z" fill="#00FF00"/>
    </svg>'''
    p = tmp_path / "in.svg"
    p.write_text(content)
    return p


def test_load_and_list(sample_svg):
    root = sve.load_svg(sample_svg)
    paths = sve.list_paths(root)
    assert len(paths) == 2
    assert paths[0]["id"] == "p1"
    assert paths[1]["fill"] == "#00FF00"


def test_set_path_attr(sample_svg, tmp_path):
    root = sve.load_svg(sample_svg)
    sve.set_path_attr(root, 0, "fill", "#0000FF")
    out = sve.save_svg(root, tmp_path / "out.svg")
    assert "#0000FF" in out.read_text()


def test_translate(sample_svg):
    root = sve.load_svg(sample_svg)
    sve.translate_path(root, 0, 10, 20)
    paths = list(root.iter("{http://www.w3.org/2000/svg}path"))
    assert "translate(10.0,20.0)" in paths[0].get("transform", "")


def test_add_shapes(sample_svg):
    root = sve.load_svg(sample_svg)
    sve.add_rect(root, 10, 10, 50, 50)
    sve.add_circle(root, 100, 100, 30)
    sve.add_text(root, 5, 5, "Hi")
    rects = list(root.iter("{http://www.w3.org/2000/svg}rect"))
    circles = list(root.iter("{http://www.w3.org/2000/svg}circle"))
    texts = list(root.iter("{http://www.w3.org/2000/svg}text"))
    assert len(rects) == 1 and len(circles) == 1 and len(texts) == 1


def test_invalid_index(sample_svg):
    root = sve.load_svg(sample_svg)
    with pytest.raises(IndexError):
        sve.set_path_attr(root, 99, "fill", "#000")
