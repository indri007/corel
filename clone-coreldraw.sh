#!/usr/bin/env bash
set -e

# ==============================================================================
# clone-coreldraw.sh
# Skrip otomatis untuk meng-clone dan menjalankan TraceDraw (Klon CorelDRAW Open Source)
# Kompatibel dengan macOS dan Linux
# ==============================================================================

echo "=== Memulai Setup TraceDraw (CorelDRAW Clone) ==="

# 1. Cek dependensi Rust / Cargo
if ! command -v cargo &> /dev/null; then
    echo "[!] Cargo / Rust belum terdeteksi. Menginstal Rust toolchain..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal
    source "$HOME/.cargo/env"
else
    echo "[✓] Rust dan Cargo sudah terinstal."
fi

# 2. Direktori proyek
REPO_URL="https://github.com/igtoth/tracedraw.git"
TARGET_DIR="tracedraw"

if [ -d "$TARGET_DIR" ]; then
    echo "[*] Folder '$TARGET_DIR' sudah ada. Memperbarui repositori..."
    cd "$TARGET_DIR"
    git pull || true
else
    echo "[*] Melakukan cloning dari $REPO_URL..."
    git clone "$REPO_URL" "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

# 3. Build & Jalankan aplikasi (release mode)
echo "[*] Menjalankan TraceDraw..."
cargo run --release -p tracedraw
