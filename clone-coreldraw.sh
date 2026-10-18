#!/usr/bin/env bash
set -e

# ==============================================================================
# clone-coreldraw.sh
# Skrip otomatisasi ekosistem CorelDRAW, Klon Open Source, Web Editors,
# Model AI Vektor, dan Library Grafis
# ==============================================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

print_header() {
    echo "================================================================="
    echo "  CorelDRAW Clones & Vector Graphics Ecosystem Automation Script"
    echo "  Repository: https://github.com/indri007/corel"
    echo "================================================================="
}

clone_repo() {
    local url="$1"
    local dir="$2"
    local extra_args="${3:-}"

    if [ -d "$dir" ]; then
        echo "[✓] Direktori '$dir' sudah ada. Melewati..."
    else
        echo "[*] Meng-clone $url ke '$dir'..."
        git clone --depth 1 $extra_args "$url" "$dir"
    fi
}

clone_hf_model() {
    local url="$1"
    local dir="$2"

    if [ -d "$dir" ]; then
        echo "[✓] Model '$dir' sudah ada. Melewati..."
    else
        echo "[*] Meng-clone metadata & kode model $url ke '$dir' (tanpa bobot raksasa)..."
        GIT_LFS_SKIP_SMUDGE=1 git clone "$url" "$dir"
    fi
}

run_tracedraw() {
    echo "=== Menjalankan TraceDraw (CorelDRAW .cdr native clone) ==="
    if [ ! -d "tracedraw" ]; then
        clone_repo "https://github.com/igtoth/tracedraw.git" "tracedraw"
    fi
    cd tracedraw
    echo "[*] Memulai kompilasi & eksekusi TraceDraw..."
    cargo run --release -p tracedraw
}

clone_desktop() {
    echo "=== Meng-clone Desktop Vector Editors ==="
    clone_repo "https://github.com/igtoth/tracedraw.git" "tracedraw"
    clone_repo "https://github.com/sk1-project/sk1-wx.git" "sk1-wx"
    clone_repo "https://github.com/rathlinus/gravit-designer.git" "gravit-designer"
    clone_repo "https://github.com/inkscape/inkscape.git" "inkscape"
    clone_repo "https://github.com/KDE/calligra.git" "calligra"
    clone_repo "https://github.com/bgrabitmap/lazpaint.git" "lazpaint"
}

clone_web() {
    echo "=== Meng-clone Web & Browser-based Vector Editors ==="
    clone_repo "https://github.com/GraphiteEditor/Graphite.git" "GraphiteEditor"
    clone_repo "https://github.com/SVG-Edit/svgedit.git" "svgedit"
    clone_repo "https://github.com/methodofaction/Method-Draw.git" "Method-Draw"
    clone_repo "https://github.com/wieslawsoltes/Vectora.git" "Vectora"
    clone_repo "https://github.com/F-star/suika.git" "suika"
    clone_repo "https://github.com/storytold/vectorcraft.git" "vectorcraft"
    clone_repo "https://github.com/penpot/penpot.git" "penpot"
}

clone_ai() {
    echo "=== Meng-clone AI Vector Models (Hugging Face) ==="
    clone_hf_model "https://huggingface.co/Caffin/SVGThinker-7B" "SVGThinker-7B"
    clone_hf_model "https://huggingface.co/xingxm/HiVG-3B-Base" "HiVG-3B-Base"
    clone_hf_model "https://huggingface.co/starvector/starvector-8b-im2svg" "starvector-8b-im2svg"
    clone_hf_model "https://huggingface.co/aoiandroid/OmniSVG1.1_4B" "OmniSVG1.1_4B"
}

clone_libs() {
    echo "=== Meng-clone Vector Libraries & Render Engines ==="
    clone_repo "https://github.com/pheralb/svgl.git" "svgl"
    clone_repo "https://github.com/visioncortex/vtracer.git" "vtracer"
    clone_repo "https://github.com/msitarzewski/vectorforge.git" "vectorforge"
    clone_repo "https://github.com/tdewolff/canvas.git" "canvas"
    clone_repo "https://github.com/jonobr1/two.js.git" "two.js"
    clone_repo "https://github.com/reznakt/svglab.git" "svglab"
    clone_repo "https://github.com/baku89/pave.git" "pave"
    clone_repo "https://codeberg.org/renfordt/php-svg.git" "php-svg"
    clone_repo "https://github.com/thorvg/thorvg.git" "thorvg"
    clone_repo "https://github.com/iconify/iconify.git" "iconify"
}

clone_all() {
    clone_desktop
    clone_web
    clone_ai
    clone_libs
    echo "[✓] Seluruh ekosistem berhasil di-clone!"
}

# Entrypoint
print_header

case "${1:-run-tracedraw}" in
    run-tracedraw)
        run_tracedraw
        ;;
    desktop)
        clone_desktop
        ;;
    web)
        clone_web
        ;;
    ai)
        clone_ai
        ;;
    libs)
        clone_libs
        ;;
    all)
        clone_all
        ;;
    help|--help|-h)
        echo "Penggunaan: ./clone-coreldraw.sh [perintah]"
        echo ""
        echo "Daftar Perintah:"
        echo "  run-tracedraw   (Default) Build dan jalankan aplikasi TraceDraw di Mac/Linux"
        echo "  desktop         Clone editor vektor desktop (TraceDraw, sK1, Inkscape, Gravit, Karbon, LazPaint)"
        echo "  web             Clone editor vektor web/PWA (Graphite, SVG-Edit, Vectora, Suika, Penpot, dll)"
        echo "  ai              Clone model AI vektor (SVGThinker-7B, HiVG-3B, StarVector, OmniSVG)"
        echo "  libs            Clone API dan rendering engine vektor (VTracer, ThorVG, SVGL, Two.js, dll)"
        echo "  all             Clone seluruh repositori ekosistem"
        ;;
    *)
        echo "[!] Perintah tidak dikenal: $1"
        echo "Gunakan './clone-coreldraw.sh help' untuk melihat bantuan."
        exit 1
        ;;
esac
