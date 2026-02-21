# 📚 SlideShare Scraper & PDF Converter

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)

**Scraping otomatis presentasi SlideShare ke format PDF berkualitas tinggi** 

*Cross-platform • High-Resolution • Auto ChromeDriver • Batch Processing*

</div>

---

## 📖 Deskripsi

**SlideShare Scraper** adalah tool Python yang powerful untuk mengunduh presentasi dari SlideShare.net dan mengkonversinya menjadi file PDF. Tool ini menggunakan Selenium dengan webdriver-manager untuk otomatis mengelola ChromeDriver, sehingga tidak perlu instalasi manual driver browser.

### ✨ Keunggulan

- 🚀 **Cross-Platform**: Berjalan di Windows dan Linux tanpa konfigurasi tambahan
- 📥 **Auto ChromeDriver**: Tidak perlu download ChromeDriver manual
- 🎯 **High-Resolution**: Mengunduh gambar berkualitas tertinggi (-2048.jpg)
- 📄 **Auto PDF Conversion**: Otomatis convert ke PDF setelah download
- ⚡ **Optimized Scrolling**: Ekstraksi cepat dengan incremental detection
- 📦 **Batch Processing**: Proses multiple URLs dalam satu run
- 🔄 **Smart Stopping**: Deteksi otomatis ketika semua slide sudah ditemukan
- 💾 **Sequential Naming**: File terorganisir dengan nama slide_001.jpg, slide_002.jpg, dll.

---

## 🎯 Fitur

| Fitur | Deskripsi |
|-------|-----------|
| **Ekstraksi Otomatis** | Scroll otomatis untuk menemukan semua slide di halaman |
| **High-Res Download** | Download gambar resolusi tertinggi (2048px) |
| **PDF Conversion** | Convert semua slide ke 1 file PDF |
| **Batch Mode** | Proses multiple presentasi sekaligus |
| **Smart Detection** | Stop otomatis jika tidak ada slide baru |
| **Cookie Handling** | Gunakan session browser untuk akses |
| **Error Handling** | Retry mechanism & detailed error messages |
| **Progress Display** | Real-time progress indicator |

---

## 📋 Persyaratan Sistem

### Software Requirements

- **Python**: 3.8 atau lebih tinggi
- **Google Chrome**: Versi terbaru (auto-update recommended)
- **Internet Connection**: Untuk download ChromeDriver dan mengakses SlideShare

### Python Dependencies

```
selenium>=4.15.0
webdriver-manager>=4.0.0
requests>=2.31.0
Pillow>=10.0.0
img2pdf>=0.5.0
```

---

## 🚀 Instalasi

### Windows

#### 1. Install Python
Download dan install Python dari [python.org](https://www.python.org/downloads/)

Pastikan centang "**Add Python to PATH**" saat instalasi!

#### 2. Install Google Chrome
Download dari [google.com/chrome](https://www.google.com/chrome/)

#### 3. Clone/Download Repository
```bash
# Via Git
git clone <repository-url>
cd Tools-Downloader

# Atau download ZIP dan extract
```

#### 4. Install Dependencies
```bash
# Buka Command Prompt atau PowerShell di folder project
pip install -r requirements.txt
```

---

### Linux (Ubuntu/Debian)

#### 1. Install Python & Chrome
```bash
# Update package list
sudo apt update

# Install Python 3 dan pip
sudo apt install python3 python3-pip -y

# Install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
```

#### 2. Clone Repository
```bash
git clone <repository-url>
cd Tools-Downloader
```

#### 3. Install Dependencies
```bash
pip3 install -r requirements.txt
```

---

## 💻 Cara Penggunaan

### Mode 1: Single URL

Edit file `main.py` dan ubah `slideshare_url` menjadi 1 URL:

```python
def main():
    slideshare_url = [
        "https://www.slideshare.net/slideshow/your-presentation-link"
    ]
    # ... rest of code
```

Jalankan:

**Windows (Command Prompt/PowerShell)**
```bash
python main.py
```

**Linux (Terminal)**
```bash
python3 main.py
```

---

### Mode 2: Batch Processing (Multiple URLs)

Edit file `main.py` untuk menambahkan multiple URLs:

```python
def main():
    slideshare_url = [
        "https://www.slideshare.net/slideshow/presentation-1",
        "https://www.slideshare.net/slideshow/presentation-2",
        "https://www.slideshare.net/slideshow/presentation-3"
    ]
    # ... rest of code
```

Jalankan dengan cara yang sama:

**Windows:**
```bash
python main.py
```

**Linux:**
```bash
python3 main.py
```

---

## 📂 Struktur Output

Setelah scraping berhasil, struktur folder:

```
Tools-Downloader/
├── main.py
├── requirements.txt
├── README.md
└── download/
    ├── Nama-Presentasi-1/
    │   ├── slide_001.jpg
    │   ├── slide_002.jpg
    │   ├── slide_003.jpg
    │   ├── ...
    │   └── Nama-Presentasi-1.pdf  ← PDF file
    │
    ├── Nama-Presentasi-2/
    │   ├── slide_001.jpg
    │   ├── ...
    │   └── Nama-Presentasi-2.pdf
    │
    └── ...
```

**Nama folder otomatis diambil dari judul presentasi** di SlideShare.

---

## ⚙️ Konfigurasi Advanced

### Mengubah Scroll Speed

Edit di `extract_image_urls()`:

```python
# Faster scrolling (lebih cepat tapi mungkin skip beberapa slide)
scroll_pause_time = 1  # Default: 2
scroll_increment = 600  # Default: 400

# Slower scrolling (lebih lengkap tapi lebih lama)
scroll_pause_time = 3
scroll_increment = 200
```

### Mengubah Image Quality

Edit di `download_images()`:

```python
# Higher quality (file lebih besar)
img.save(filepath, 'JPEG', quality=100, optimize=True)

# Lower quality (file lebih kecil)
img.save(filepath, 'JPEG', quality=85, optimize=True)
```

### Mengubah Timeout

Edit di `setup_driver()`:

```python
self.driver.set_page_load_timeout(120)  # Default: 60 seconds
```

---

## 🔧 Troubleshooting

### ❌ Error: "ChromeDriver not found"

**Solusi:**
- Pastikan Google Chrome sudah terinstall
- Pastikan `webdriver-manager` sudah terinstall:
  ```bash
  pip install webdriver-manager --upgrade
  ```

---

### ❌ Error: "No module named 'selenium'"

**Solusi:**
- Install ulang dependencies:
  ```bash
  pip install -r requirements.txt
  ```

---

### ❌ Error: "TimeoutException"

**Solusi:**
- Periksa koneksi internet
- Coba jalankan ulang script
- Tingkatkan timeout di konfigurasi

---

### ❌ Tidak ada slide yang terdeteksi

**Solusi:**
- Pastikan URL SlideShare valid dan bisa diakses
- Coba akses URL di browser manual dulu
- Beberapa presentasi mungkin private/restricted

---

### ❌ Error: "SSL Certificate Verify Failed"

**Solusi Linux:**
```bash
pip3 install --upgrade certifi
```

**Solusi Windows:**
```bash
pip install --upgrade certifi
```

---

## 📊 Contoh Output

```
================================================================================
🚀 BATCH SLIDESHARE SCRAPER (Optimized + Auto PDF)
================================================================================

Total URLs to process: 3
Features:
  • Fast scroll (400px/2s) with incremental extraction
  • High-res images only (-2048.jpg quality)
  • Direct download with sequential naming (slide_001.jpg, slide_002.jpg, ...)
  • Auto-convert to single PDF file after download
  • Smart stopping (no new images for 3 iterations)

[1/3] Processing URL...
⚙️  Initializing Chrome driver...
✅ Chrome driver started

🌐 Opening SlideShare link...
✅ Page loaded successfully
📄 File name extracted: Materi PPT Bentuk Aljabar Kelas 7

🔍 Extracting image URLs via optimized scroll...
   📸 Found 25 high-res slides (+25)
✅ Image URLs extracted: 25 slides

💾 DOWNLOADING HIGH-RES IMAGES (Direct Download)
[1/25] Downloading: slide_001.jpg... ✅ 245,832 bytes
[2/25] Downloading: slide_002.jpg... ✅ 198,654 bytes
...
✅ Successfully downloaded 25/25 images

📄 CONVERTING TO PDF
✅ PDF created successfully!
   File: Materi PPT Bentuk Aljabar Kelas 7.pdf
   Size: 5.82 MB
   Pages: 25

✅ SCRAPING COMPLETED SUCCESSFULLY!
```

---

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan:

1. Fork repository ini
2. Buat branch fitur baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

---

## 🐛 Laporkan Bug

Jika menemukan bug, silakan buat issue di repository dengan detail:

- Sistem operasi (Windows/Linux)
- Versi Python
- Error message lengkap
- URL SlideShare yang digunakan (jika bisa)
- Screenshot (jika perlu)

---

## 📝 License

Project ini menggunakan MIT License - lihat file [LICENSE](LICENSE) untuk detail.

---

## ⚠️ Disclaimer

Tool ini dibuat untuk tujuan edukasi dan penggunaan pribadi. Pastikan Anda memiliki hak untuk mengunduh dan menggunakan konten dari SlideShare. Hormati hak cipta pemilik konten.

**Gunakan dengan bijak dan bertanggung jawab!**

---

## 🙏 Acknowledgments

- [Selenium](https://www.selenium.dev/) - Web automation framework
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) - Automatic ChromeDriver management
- [img2pdf](https://gitlab.mister-muffin.de/josch/img2pdf) - Image to PDF conversion
- [Pillow](https://python-pillow.org/) - Image processing

---

## 📞 Kontak

Jika ada pertanyaan atau saran, silakan buat issue di repository atau hubungi maintainer.

---

<div align="center">

**Made with ❤️ for Ramadhan Code Fest 2026**

⭐ Jangan lupa star repository ini jika bermanfaat! ⭐

</div>
