"""Setup logging terstruktur untuk aplikasi."""
from __future__ import annotations
import logging, sys

def setup_logging(level: int = logging.INFO) -> None:
    """Konfigurasi root logger sekali saja."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    ))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
