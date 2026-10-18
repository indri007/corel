# Panduan Teknis: Instalasi CorelDRAW & Membangun Klon Open-Source (TraceDraw)

Dokumen ini menyajikan panduan teknis mendalam mengenai dua konteks yang sering dimaksud ketika membahas **"Clone CorelDRAW"**:

1. **Instalasi & Deployment Massal CorelDRAW Resmi (Windows)**: Melakukan instalasi otomatis tanpa tampilan antarmuka pengguna (*silent/unattended install*) menggunakan switch baris perintah (*command line*).
2. **Membangun Editor Klon CorelDRAW Open-Source (TraceDraw)**: Membangun dan menjalankan editor grafis vektor open-source berbasis bahasa pemrograman Rust yang mampu membuka dan memproses format berkas `.cdr`.

---

> [!IMPORTANT]
> **Pembedaan Konteks Sistem Operasi:**
> - **Bagian A (CorelDRAW Asli)** ditujukan untuk lingkungan **Windows** (menggunakan berkas eksekusi biner `Setup.exe`).
> - **Bagian B (TraceDraw)** bersifat **Multi-platform** (dapat di-compile dan dijalankan di **macOS**, **Linux**, **Windows**, serta di dalam **Web Browser** via WebAssembly).

---

## Bagian A: Instalasi CorelDRAW Resmi via Command Line (Windows)

Metode ini umum digunakan oleh administrator sistem (*sysadmin*) dan teknisi TI untuk menyebarkan (*deploy*) CorelDRAW Graphics Suite ke banyak workstation secara otomatis tanpa interaksi pengguna.

### 1. Perintah Dasar Silent Install
Untuk menjalankan instalasi tanpa menampilkan antarmuka konfigurasi interaktif, gunakan switch `/qn` (Quiet No-UI):

```cmd
Setup.exe /qn
```

*Catatan Switch Tambahan:*
- `/qb` : Menampilkan UI dasar (*progress bar* saja tanpa meminta input pengguna).
- `SERIALNUMBER="XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"` : Memasukkan lisensi serial secara langsung saat instalasi.

---

### 2. Memilih Komponen dengan Parameter `ADDLOCAL`
Parameter `ADDLOCAL` memungkinkan Anda memilih modul atau fitur spesifik yang ingin dipasang:

```cmd
:: Contoh 1: Hanya menginstal Corel DESIGNER dan Windows Shell Extension (penampil thumbnail .cdr di explorer)
Setup.exe /qn ADDLOCAL=Designer SHELLEXT=1

:: Contoh 2: Instalasi CorelDRAW utama bersama komponen GPL Ghostscript
Setup.exe /qn ADDLOCAL=Draw GPL=1
```

*Daftar Fitur Populer `ADDLOCAL`:*
- `Draw` : CorelDRAW (Editor Vektor Utama).
- `PHOTO-PAINT` : Corel PHOTO-PAINT (Editor Gambar Bitmap).
- `Capture` : Corel CAPTURE.
- `Designer` : Corel DESIGNER (Ilustrasi Teknis).
- `FontManager` : Corel Font Manager.
- `SHELLEXT` : Integrasi Windows Shell Extension (pratinjau thumbnail file `.cdr`).
- `GPL` : Modul pendukung penerjemah PostScript berbasis GPL.

---

### 3. Mencatat Log Instalasi (*Logging*)
Untuk kebutuhan audit dan pelacakan kesalahan saat proses instalasi di latar belakang, sertakan parameter pencatatan berkas log (`/L`):

```cmd
Setup.exe /qn /L "C:\Logs\Corel_Install.log"
```

Jika memerlukan log detail (*verbose*):
```cmd
Setup.exe /qn /L*v "C:\Logs\Corel_Install_Verbose.log"
```

---

### 4. Catatan Khusus CorelDRAW 2022 ke Atas: Server Image & Perintah `/a`
Pada CorelDRAW versi modern (2022, 2023, 2024 ke atas):
- Parameter `/a` digunakan untuk membuat **Server Image** (Administrative Deployment Image) di folder bersama jaringan (*network share*):
  ```cmd
  X:\x64\Setup.exe /a
  ```
- **Struktur Jalur `x64`**: Pada media instalasi versi modern, berkas `Setup.exe` utama biasanya terletak di dalam subdirektori arsitektur `x64\`.
- **Integritas Lisensi Korporat**: Perintah `/a` membutuhkan serial key korporat/volume licensing (*Multi-Seat License*). Setelah gambar server terbentuk di folder bersama (misal `\\server\share\Corel`), klien dapat menjalankan instalasi langsung dari folder tersebut tanpa media fisik.

---

### 5. Prasyarat Tambahan (Prerequisites)
Sebelum menjalankan instalasi massal, pastikan dependensi berikut sudah tersedia pada sistem target:
1. **GPL Ghostscript**: Dibutuhkan untuk membaca, mengimpor, dan mengekspor berkas EPS dan PostScript (PS) berformat terbuka.
2. **Microsoft VSTA (Visual Studio Tools for Applications)** / **VBA**: Diperlukan jika alur kerja Anda memanfaatkan skrip otomatisasi makro (*Macros*) di CorelDRAW.
3. **Microsoft Visual C++ Redistributable**: Runtime C++ (2015–2022) harus terpasang agar modul biner CorelDRAW dapat berjalan stabil.

---

## Bagian B: Membangun Clone CorelDRAW Open-Source (TraceDraw)

**TraceDraw** adalah proyek *clean-room implementation* editor grafik vektor yang dibangun dari nol menggunakan bahasa pemrograman **Rust**. TraceDraw memiliki keunggulan utama berupa kemampuan membaca format berkas asli CorelDRAW (`.cdr` versi 3 hingga 22) dan menulis berkas `.cdr` (versi 7 hingga 22).

### 1. Prasyarat Sistem & Dependensi

#### A. Rust Toolchain (Semua Platform)
Pastikan Rust compiler (`rustc`) dan package manager (`cargo`) sudah terpasang:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
```

#### B. Dependensi Library Grafis (Khusus Linux / Ubuntu / Debian)
TraceDraw membutuhkan library sistem untuk antarmuka jendela (X11 & Wayland), penanganan input keyboard, dan akselerasi grafis OpenGL/Mesa:
```bash
sudo apt update && sudo apt install -y \
    build-essential \
    cmake \
    clang \
    libasound2-dev \
    libx11-dev \
    libxrandr-dev \
    libxi-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxcursor-dev \
    libxinerama-dev \
    libwayland-dev \
    libxkbcommon-dev
```
*(Catatan: Untuk pengguna **macOS**, library di atas tidak diperlukan karena macOS menggunakan native Cocoa, Metal, dan CoreAudio yang sudah terintegrasi pada sistem operasi).*

---

### 2. Meng-clone Repositori TraceDraw
Unduh repositori kode sumber resmi:
```bash
git clone https://github.com/igtoth/tracedraw.git
cd tracedraw
```

---

### 3. Build & Menjalankan Aplikasi

#### Mode Desktop (Release Build)
Untuk mendapatkan performa optimal saat menggambar vektor:
```bash
cargo run --release -p tracedraw
```

#### Membuka Berkas `.cdr` Secara Langsung:
```bash
cargo run --release -p tracedraw -- nama_desain.cdr
```

#### Menjalankan Versi Web (Browser via WebAssembly):
TraceDraw dapat dikompilasi menjadi WebAssembly untuk dijalankan di browser tanpa instalasi:
```bash
# Tambahkan target wasm
rustup target add wasm32-unknown-unknown

# Pasang wasm-bindgen versi yang sesuai
cargo install wasm-bindgen-cli --version 0.2.129

# Eksekusi build script web
./scripts/web/build.sh

# Sajikan melalui server HTTP lokal
python3 -m http.server -d site 8080
```
Buka browser di `http://localhost:8080`.

---

### 4. Menjalankan Pengujian (*Test Suite*)
Untuk memastikan seluruh modul parser berkas `.cdr`, mesin teks, dan kalkulasi kurva vektor berfungsi dengan benar:
```bash
# Menjalankan seluruh test
cargo test

# Menjalankan test spesifik untuk modul pembaca .cdr
cargo test -p tracedraw-cdr
```

---

## Ringkasan Perbandingan

| Kategori | Instalasi CorelDRAW Asli | Klon Open-Source (TraceDraw) |
|---|---|---|
| **Tujuan** | Menyebarkan perangkat lunak resmi Corel | Membangun editor vektor open-source independen |
| **Sistem Operasi** | Windows (x64) | Lintas Platform (macOS, Linux, Windows, Web) |
| **Lisensi** | Komersial Berbayar (Proprietary) | Open Source (MIT / Apache-2.0) |
| **Alat Utama** | `Setup.exe`, MSI Installer | Rust, Cargo, `wasm-bindgen` |
| **Dukungan `.cdr`** | Asli Penuh | Kompatibel *clean-room* (baca v3–v22, tulis v7–v22) |