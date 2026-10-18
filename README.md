# Ekosistem CorelDRAW, Klon Open-Source, Web Editors & Vektor AI

Repositori ini menyajikan panduan teknis mendalam dan kumpulan ekosistem lengkap seputar **CorelDRAW**, alternatif editor vektor open-source, editor grafis berbasis web (PWA/Canvas/WebGPU), model kecerdasan buatan (AI) pembuat vektor/SVG, serta pustaka (*library*) pemrosesan grafis vektor modern.

---

> [!IMPORTANT]
> **Pembedaan Konteks Sistem Operasi:**
> - **Bagian 1 (CorelDRAW Asli)** ditujukan untuk lingkungan **Windows** (menggunakan berkas eksekusi biner `Setup.exe`).
> - **Bagian 2 - 6 (Klon Open-Source, Web, & AI)** bersifat **Multi-platform** (berjalan di **macOS**, **Linux**, **Windows**, serta di dalam **Web Browser**).

---

## 📑 Daftar Isi
1. [Instalasi CorelDRAW Resmi via Command Line (Windows)](#1-instalasi-coreldraw-resmi-via-command-line-windows)
2. [Membangun Klon CorelDRAW: TraceDraw (Rust)](#2-membangun-klon-coreldraw-tracedraw-rust)
3. [Katalog Klon & Editor Vektor Desktop Open-Source](#3-katalog-klon--editor-vektor-desktop-open-source)
4. [Katalog Editor Vektor Berbasis Web & Browser (PWA/Canvas/WebGPU)](#4-katalog-editor-vektor-berbasis-web--browser-pwacanvaswebgpu)
5. [Model AI Foundation untuk Grafis Vektor & SVG (Hugging Face)](#5-model-ai-foundation-untuk-grafis-vektor--svg-hugging-face)
6. [API, Rendering Engine, & Library Manipulasi Vektor](#6-api-rendering-engine--library-manipulasi-vektor)
7. [Panduan Skrip Otomatisasi (clone-coreldraw.sh)](#7-panduan-skrip-otomatisasi-clone-coreldrawsh)

---

## 1. Instalasi CorelDRAW Resmi via Command Line (Windows)

Metode ini digunakan oleh administrator sistem untuk menyebarkan (*deploy*) CorelDRAW Graphics Suite secara otomatis (*silent/unattended install*).

### A. Perintah Dasar Silent Install
```cmd
Setup.exe /qn
```
- `/qn` : *Quiet No-UI* (berjalan sepenuhnya di latar belakang tanpa dialog antarmuka).
- `/qb` : *Quiet Basic UI* (hanya menampilkan indikator bilah kemajuan / *progress bar* sederhana).
- `SERIALNUMBER="XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"` : Memasukkan nomor lisensi secara langsung.

### B. Memilih Komponen dengan `ADDLOCAL`
```cmd
:: Contoh 1: Hanya menginstal Corel DESIGNER dan Windows Shell Extension
Setup.exe /qn ADDLOCAL=Designer SHELLEXT=1

:: Contoh 2: Instalasi CorelDRAW utama bersama modul GPL Ghostscript
Setup.exe /qn ADDLOCAL=Draw GPL=1
```
*Daftar Fitur `ADDLOCAL`:*
- `Draw` : Editor Vektor CorelDRAW.
- `PHOTO-PAINT` : Editor bitmap Corel PHOTO-PAINT.
- `Designer` : Corel DESIGNER (Ilustrasi teknis).
- `FontManager` : Manajemen tipografi Corel Font Manager.
- `SHELLEXT` : Integrasi Windows Shell Extension (pratinjau thumbnail file `.cdr`).
- `GPL` : Modul penerjemah berkas PostScript berbasis GPL.

### C. Mencatat Log Instalasi (*Logging*)
```cmd
Setup.exe /qn /L "C:\Logs\Corel_Install.log"
```
Untuk log verbose mendalam:
```cmd
Setup.exe /qn /L*v "C:\Logs\Corel_Install_Verbose.log"
```

### D. Catatan Khusus CorelDRAW 2022 ke Atas (Server Image & `/a`)
Pada versi modern (2022, 2023, 2024+):
```cmd
X:\x64\Setup.exe /a
```
- Berkas biner `Setup.exe` terletak di subfolder `\x64\`.
- Parameter `/a` digunakan untuk membuat *Administrative Server Image* di folder bersama jaringan (*network share*) untuk volume licensing / multi-seat corporate deployment.

### E. Prasyarat Sistem Tambahan
- **GPL Ghostscript**: Untuk memproses berkas EPS & PostScript (PS).
- **Microsoft VSTA / VBA**: Diperlukan jika memanfaatkan otomatisasi makro.
- **Microsoft Visual C++ Redistributable (2015–2022)**.

---

## 2. Membangun Klon CorelDRAW: TraceDraw (Rust)

**TraceDraw** adalah proyek *clean-room* editor vektor berbasis bahasa pemrograman **Rust** yang dapat membaca berkas `.cdr` (CorelDRAW versi 3–22) dan menulis berkas `.cdr` (versi 7–22).

### A. Prasyarat Sistem
- **Rust Toolchain**: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y`
- **Linux Dev Libs**:
  ```bash
  sudo apt update && sudo apt install -y build-essential cmake clang libasound2-dev libx11-dev libxrandr-dev libxi-dev libgl1-mesa-dev libglu1-mesa-dev libxcursor-dev libxinerama-dev libwayland-dev libxkbcommon-dev
  ```
  *(Pengguna macOS tidak memerlukan paket Linux di atas karena menggunakan Cocoa/Metal bawaan).*

### B. Clone, Build, & Run
```bash
git clone https://github.com/igtoth/tracedraw.git
cd tracedraw

# Menjalankan aplikasi desktop (release mode)
cargo run --release -p tracedraw

# Membuka file .cdr langsung
cargo run --release -p tracedraw -- desain.cdr

# Menjalankan pengujian (test suite)
cargo test
cargo test -p tracedraw-cdr
```

### C. Menjalankan di Browser (WebAssembly)
```bash
rustup target add wasm32-unknown-unknown
cargo install wasm-bindgen-cli --version 0.2.129
./scripts/web/build.sh
python3 -m http.server -d site 8080
```

---

## 3. Katalog Klon & Editor Vektor Desktop Open-Source

| Perangkat Lunak | Repositori / Sumber | Bahasa / Stack | Deskripsi & Kegunaan |
|---|---|---|---|
| **TraceDraw** | [igtoth/tracedraw](https://github.com/igtoth/tracedraw) | Rust | Editor vektor *clean-room* dengan dukungan native membaca & menulis format berkas `.cdr`. |
| **sK1** | [sk1-project/sk1-wx](https://github.com/sk1-project/sk1-wx) | Python, C, wxWidgets | Alternatif CorelDRAW open-source legendaris dengan manajemen warna CMYK tingkat profesional dan importir `.cdr`. |
| **Gravit Designer (Offline)** | [rathlinus/gravit-designer](https://github.com/rathlinus/gravit-designer) | JavaScript, Electron | Versi lokal mandiri dari Corel Vector (dahulu Gravit Designer) dengan fitur Pro offline tanpa akun cloud. |
| **Inkscape** | [inkscape/inkscape](https://github.com/inkscape/inkscape) | C++, GTK | Editor vektor open-source standar industri dengan format native SVG. |
| **Karbon (Calligra)** | [KDE/calligra](https://github.com/KDE/calligra) | C++, Qt, KDE Frameworks | Komponen ilustrasi vektor dari KDE Calligra Suite untuk pembuatan ilustrasi, logo, dan diagram. |
| **LazPaint** | [bgrabitmap/lazpaint](https://github.com/bgrabitmap/lazpaint) | Pascal, BGRABitmap | Editor grafis raster dan vektor ringan dengan kurva Bezier, layer, dan filter visual. |

---

## 4. Katalog Editor Vektor Berbasis Web & Browser (PWA/Canvas/WebGPU)

| Aplikasi | Repositori | Teknologi | Deskripsi |
|---|---|---|---|
| **Graphite** | [GraphiteEditor/Graphite](https://github.com/GraphiteEditor/Graphite) | Rust, WebAssembly, WebGL | Editor 2D prosedural berbasis node ("Blender-nya 2D") yang berjalan sebagai PWA di browser. |
| **SVG-Edit** | [SVG-Edit/svgedit](https://github.com/SVG-Edit/svgedit) | JavaScript | Editor SVG open-source berbasis browser paling populer yang telah berumur 15+ tahun. |
| **Method Draw** | [methodofaction/Method-Draw](https://github.com/methodofaction/Method-Draw) | JavaScript | Fork SVG-Edit yang disederhanakan dengan antarmuka elegan untuk pengeditan cepat. |
| **Vectora** | [wieslawsoltes/Vectora](https://github.com/wieslawsoltes/Vectora) | JS, WGSL, WebGPU | Editor vektor berbasis WebGPU tanpa framework dan tanpa instalasi npm. |
| **Suika** | [F-star/suika](https://github.com/F-star/suika) | TypeScript, HTML5 Canvas | Editor vektor infinite-canvas dengan alur kerja mirip Figma. |
| **VectorCraft** | [storytold/vectorcraft](https://github.com/storytold/vectorcraft) | Rust, WebAssembly | Reimplementasi alur kerja Adobe Illustrator menggunakan Rust murni yang berjalan di web. |
| **Penpot** | [penpot/penpot](https://github.com/penpot/penpot) | Clojure, TypeScript, SVG | Platform desain UI/UX dan prototipe open-source dengan standar terbuka SVG dan CSS. |
| **CorelClone Pro** | [alternativeto.net](https://alternativeto.net/software/corelclone-pro/about/) | Web / PWA | Studio desain vektor PWA terinspirasi CorelDRAW dengan fitur penelusuran bitmap (PowerTRACE). |

---

## 5. Model AI Foundation untuk Grafis Vektor & SVG (Hugging Face)

| Model | Repositori HF | Ukuran | Kemampuan Utama |
|---|---|---|---|
| **SVGThinker-7B** | [Caffin/SVGThinker-7B](https://huggingface.co/Caffin/SVGThinker-7B) | 7B | LLM reasoning khusus untuk menghasilkan dan mengoptimasi kode vektor SVG kompleks. |
| **HiVG-3B-Base** | [xingxm/HiVG-3B-Base](https://huggingface.co/xingxm/HiVG-3B-Base) | 3B | Model pemrosesan grafis vektor hierarkis (*Hierarchical Vector Graphics*). |
| **StarVector-8B-im2svg** | [starvector/starvector-8b-im2svg](https://huggingface.co/starvector/starvector-8b-im2svg) | 8B | Foundation model yang mengonversi gambar raster atau teks menjadi instruksi SVG presisi tinggi. |
| **OmniSVG 1.1** | [aoiandroid/OmniSVG1.1_4B](https://huggingface.co/aoiandroid/OmniSVG1.1_4B) | 4B | Model multimodal untuk inferensi dan pembuatan aset vektor SVG multi-domain. |

---

## 6. API, Rendering Engine, & Library Manipulasi Vektor

| Nama Library / Tool | Repositori | Bahasa / Format | Fungsi Utama |
|---|---|---|---|
| **VTracer** | [visioncortex/vtracer](https://github.com/visioncortex/vtracer) | Rust, WASM, Node.js | Konverter raster ke vektor SVG full-color super cepat (alternatif Corel PowerTRACE). |
| **VectorForge** | [msitarzewski/vectorforge](https://github.com/msitarzewski/vectorforge) | Python (FastAPI) | REST API raster-to-vector dengan validasi metrik kualitas hasil konversi. |
| **ThorVG** | [thorvg/thorvg](https://github.com/thorvg/thorvg) | C++, WebGPU | Engine vektor produksi berkinerja tinggi untuk merender SVG dan animasi Lottie. |
| **SVGL** | [pheralb/svgl](https://github.com/pheralb/svgl) | TypeScript, REST API | Katalog 400+ logo merek berformat SVG dengan REST API publik (`api.svgl.app`). |
| **tdewolff/canvas** | [tdewolff/canvas](https://github.com/tdewolff/canvas) | Go | Mesin gambar vektor Go untuk ekspor SVG, PDF, EPS dengan operasi boolean path. |
| **Two.js** | [jonobr1/two.js](https://github.com/jonobr1/two.js) | JavaScript | API gambar 2D renderer-agnostic (SVG, Canvas, WebGL) dengan SVG interpreter bawaan. |
| **SVGLab** | [reznakt/svglab](https://github.com/reznakt/svglab) | Python | Pustaka parsing, manipulasi kurva, dan optimasi struktur berkas SVG. |
| **@baku89/pave** | [baku89/pave](https://github.com/baku89/pave) | TypeScript | Toolkit manipulasi kurva SVG/Path2D (offsetting, resampling, normal/tangen). |
| **PHP-SVG** | [codeberg.org/renfordt/php-svg](https://codeberg.org/renfordt/php-svg) | PHP | Library vektor zero-dependency untuk membuat dan merasterisasi SVG di sisi backend. |
| **Iconify** | [iconify/iconify](https://github.com/iconify/iconify) | TypeScript, Node.js | Kerangka kerja ikon terpadu dengan 200,000+ ikon vektor dan REST API. |

---

## 7. Panduan Skrip Otomatisasi (`clone-coreldraw.sh`)

Gunakan skrip [clone-coreldraw.sh](file:///Users/jevin/corel/clone-coreldraw.sh) yang disertakan dalam repositori untuk mengunduh dan menjalankan ekosistem yang dibutuhkan:

```bash
# Memberi izin eksekusi
chmod +x clone-coreldraw.sh

# 1. Menjalankan TraceDraw (default)
./clone-coreldraw.sh run-tracedraw

# 2. Meng-clone semua editor desktop
./clone-coreldraw.sh desktop

# 3. Meng-clone semua editor web / browser
./clone-coreldraw.sh web

# 4. Meng-clone model AI vektor (metadata & kode tanpa bobot puluhan GB)
./clone-coreldraw.sh ai

# 5. Meng-clone semua library & render engine
./clone-coreldraw.sh libs

# 6. Meng-clone seluruh ekosistem sekaligus
./clone-coreldraw.sh all
```