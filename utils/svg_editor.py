"""Editor vektor minimal: muat SVG, edit path, ekspor ulang."""
from __future__ import annotations

import logging
from pathlib import Path
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def load_svg(path: str | Path) -> ET.Element:
    """Muat SVG sebagai ElementTree."""
    return ET.parse(str(path)).getroot()


def save_svg(root: ET.Element, path: str | Path) -> Path:
    """Simpan ElementTree sebagai SVG."""
    out = Path(path)
    ET.ElementTree(root).write(str(out), encoding="utf-8", xml_declaration=True)
    return out


def list_paths(root: ET.Element) -> list[dict]:
    """Daftar semua path dengan id, d, fill, stroke."""
    result = []
    for i, el in enumerate(root.iter(f"{{{SVG_NS}}}path")):
        result.append({
            "index": i,
            "id": el.get("id", f"path_{i}"),
            "d": el.get("d", ""),
            "fill": el.get("fill", "none"),
            "stroke": el.get("stroke", "none"),
            "stroke-width": el.get("stroke-width", "1"),
        })
    return result


def set_path_attr(root: ET.Element, index: int, key: str, value: str) -> ET.Element:
    """Ubah atribut path ke-index (fill, stroke, stroke-width, d)."""
    paths = list(root.iter(f"{{{SVG_NS}}}path"))
    if index < 0 or index >= len(paths):
        raise IndexError(f"Path index {index} tidak ada (total {len(paths)})")
    paths[index].set(key, value)
    return root


def translate_path(root: ET.Element, index: int, dx: float, dy: float) -> ET.Element:
    """Geser path via transform matrix."""
    paths = list(root.iter(f"{{{SVG_NS}}}path"))
    if index < 0 or index >= len(paths):
        raise IndexError(f"Path index {index} tidak ada")
    p = paths[index]
    existing = p.get("transform", "")
    p.set("transform", f"{existing} translate({float(dx)},{float(dy)})".strip())
    return root


def add_rect(root: ET.Element, x: float, y: float, w: float, h: float,
             fill: str = "#C8102E") -> ET.Element:
    """Tambah rectangle vektor."""
    rect = ET.SubElement(root, f"{{{SVG_NS}}}rect")
    rect.set("x", str(x)); rect.set("y", str(y))
    rect.set("width", str(w)); rect.set("height", str(h))
    rect.set("fill", fill)
    return root


def add_circle(root: ET.Element, cx: float, cy: float, r: float,
               fill: str = "#1A1A1A") -> ET.Element:
    """Tambah circle vektor."""
    c = ET.SubElement(root, f"{{{SVG_NS}}}circle")
    c.set("cx", str(cx)); c.set("cy", str(cy)); c.set("r", str(r))
    c.set("fill", fill)
    return root


def add_text(root: ET.Element, x: float, y: float, text: str,
             font_size: int = 24, fill: str = "#000000") -> ET.Element:
    """Tambah elemen teks vektor."""
    t = ET.SubElement(root, f"{{{SVG_NS}}}text")
    t.set("x", str(x)); t.set("y", str(y))
    t.set("font-size", str(font_size)); t.set("fill", fill)
    t.set("font-family", "sans-serif")
    t.text = text
    return root


def svg_to_data_uri(path: str | Path) -> str:
    """Konversi SVG ke data URI untuk ditampilkan inline di HTML."""
    import base64
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode()
    return f"data:image/svg+xml;base64,{b64}"
