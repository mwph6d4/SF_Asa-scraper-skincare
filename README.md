# 🌸 Asa Beauty - Web Scraper Kosmetik

Proyek ini adalah aplikasi web berbasis Flask yang dirancang untuk melakukan *scraping* data produk kosmetik dari situs **Sociolla.com**. Pengguna dapat mendaftar, melakukan *scraping* produk dari berbagai merek, menyimpan hasilnya ke dalam database pribadi, melihat produk-produk dengan detail lengkap (termasuk harga asli dan diskon), serta mengelola data yang telah dikumpulkan.

Aplikasi ini dibangun sebagai tugas akhir/proyek Web Programming untuk menunjukkan integrasi teknologi *backend* (Flask), *web scraping* (Selenium & BeautifulSoup), dan manajemen database (SQLAlchemy).

---

## ✈️ Fitur Utama

Berikut ini adalah fitur-fitur yang ada dalam website Asa Beauty:

* **Autentikasi Pengguna**
    * Sistem Register dan Login sederhana.
    * Setiap *user* memiliki riwayat *scraping* yang tercatat secara terpisah.
    * Hanya *user* yang *login* yang bisa mengakses halaman *scraping* dan profil.
    * Notifikasi *login* berhasil/gagal menggunakan SweetAlert2.

* **Scraping Data Produk**
    * Melakukan *scraping* data produk dari **Sociolla.com** berdasarkan kata kunci merek (misalnya Wardah, Somethinc).
    * Menggunakan **Selenium** dan **BeautifulSoup4** untuk mengekstrak informasi detail seperti nama produk, harga (bersih, asli, hemat), *brand*, *rating*, dan **deskripsi produk** dari halaman detail.
    * Mengatasi tantangan *lazy loading* dan variasi struktur harga di *website* target.
    * Produk `e-gift-card` (seperti "Pretty Things For You") secara otomatis difilter dan tidak ditampilkan.
    * **Scraping Banner Otomatis:** Mengambil URL gambar banner dari Sociolla dan menampilkannya sebagai *carousel* di halaman utama.

* **Penyimpanan & Tampilan Data**
    * Menyimpan hasil *scraping* ke database **SQLite** menggunakan Flask-SQLAlchemy.
    * Data produk ditampilkan di halaman utama dengan pagination (20 produk per halaman).
    * Halaman detail produk menampilkan semua informasi yang di-*scrape*, termasuk deskripsi dan kolom komentar.

* **Interaksi Pengguna**
    * Fitur pencarian untuk memfilter produk yang sudah ada di database berdasarkan *keyword*.
    * Pengguna dapat menambahkan komentar pribadi pada setiap produk yang di-*scrape* di halaman detail.
    * Nama pengguna tampil di pojok kanan atas setelah *login*.

---

## 🌐 Teknologi Yang Digunakan

* **Backend:** Python, Flask
* **Database:** SQLite, Flask-SQLAlchemy
* **Web Scraping:** Selenium, BeautifulSoup4
* **Data Handling:** Pandas
* **Frontend:** HTML, Tailwind CSS, JavaScript, Swiper.js (untuk *carousel* banner)
* **Lainnya:** Flask-Login (untuk autentikasi), Werkzeug.security (untuk *hashing password*), SweetAlert2 (untuk notifikasi).

---

## 📂 Struktur Project

Berikut adalah struktur file dan folder dari proyek ini:

AsaBeauty/
AsaBeauty/
├── .venv/
│   ├── lib/
│   ├── include/
│   └── Scripts/
│       └── ...
├── scraped_data/
│   └── sociolla_wardah_products.csv
├── static/
│   └── images/
│       ├── banner1.jpg
│       ├── banner2.jpg
│       └── logoweb.png
├── templates/
│   ├── layout.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── scrape_page.html
│   ├── profile.html
│   ├── product_detail.html
│   └── search_results.html
├── app.py
├── config.py
├── extensions.py
├── forms.py
├── models.py
├── routes.py
└── scrape.py


---

## 🚀 Cara Instalasi dan Menjalankan Project

Berikut adalah langkah-langkah untuk menjalankan proyek ini di lingkungan lokal Anda.

### 1. Syarat Instalasi

* **Python 3.8 atau yang terbaru**
* **pip** (Python Package Installer)
* **Google Chrome** (Pastikan versi Google Chrome Anda *up-to-date*)
* **ChromeDriver** (Pastikan versi ChromeDriver cocok dengan versi Google Chrome Anda. Unduh dari [https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)). Letakkan `chromedriver.exe` di lokasi yang mudah diakses dan perbarui path-nya di `routes.py` jika perlu.
* **Git** (untuk *clone repository*)

### 2. Langkah-Langkah Instalasi

1.  **Clone Repository:**
    Buka terminal atau Command Prompt, lalu *clone* repository ini dari Github:
    ```bash
    git clone <URL Github Repository Anda>
    cd <nama-folder-repository-anda>
    ```

2.  **Buat dan Aktifkan Virtual Environment:**
    Buat *virtual environment* baru di dalam direktori proyek Anda dan aktifkan:
    ```bash
    # Membuat environment .venv
    python -m venv .venv
    ```
    Aktifkan *environment* tersebut (lakukan ini setiap kali Anda membuka terminal baru untuk proyek ini):
    * **Untuk Windows (Command Prompt/PowerShell):**
        ```bash
        .\venv\Scripts\activate
        ```
    * **Untuk Linux/macOS (Bash/Zsh):**
        ```bash
        source venv/bin/activate
        ```

3.  **Install Dependencies:**
    Install semua *library* Python yang dibutuhkan dengan *prompt* berikut (pastikan *virtual environment* aktif):
    ```bash
    pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug Flask-WTF WTForms pandas beautifulsoup4 selenium
    ```
    Tunggu hingga semua instalasi selesai tanpa *error*.

### 3. Persiapan File Statis (Banner Lokal Anda)

* **Buat folder:** `static/images/` di dalam direktori *root* proyek Anda.
* **Salin file banner Anda:** Letakkan file banner Anda (misalnya `banner1.jpg` dan `banner2.jpg`) ke dalam folder `static/images/`.
* **Perbarui `routes.py`:** Buka `routes.py` dan pastikan bagian `local_banner_urls` di dalam fungsi `run_scrape` mencantumkan nama file banner Anda dengan ekstensi yang benar (`.jpg` atau `.png`). Contohnya:
    ```python
    local_banner_urls = [
        url_for('static', filename='images/banner1.jpg'),
        url_for('static', filename='images/banner2.jpg')
    ]
    ```

### 4. Bersihkan Database Lama (Penting!)

Sebelum menjalankan aplikasi, hapus database lama untuk memastikan skema terbaru diterapkan dan data baru di-*scrape*.

```bash
Hentikan server Flask jika sedang berjalan (Ctrl+C)
Hapus file database.db di root folder proyek Anda
rm database.db   # Untuk Linux/macOS
del database.db  # Untuk Windows

5. Jalankan Aplikasi
Buka terminal VSCode Anda (dengan virtual environment aktif), lalu pastikan direktori sudah benar. Setelah itu jalankan prompt ini.

Bash

python app.py
Setelah itu akan muncul output di terminal Anda seperti contoh ini:

* Serving Flask app 'app'
* Debug mode: on
Database created or already exists!
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
* Running on [http://127.0.0.1:5000](http://127.0.0.1:5000)
Press CTRL+C to exit
Arahkan kursor pada link http://127.0.0.1:5000, maka akan muncul link server website. Klik dan Anda akan tiba di halaman beranda website.

6. Jalankan Proses Scraping Pertama
Karena database baru dan kosong, Anda perlu menjalankan scraping pertama kali untuk mengisi data.

Di browser, navigasikan ke http://127.0.0.1:5000/run_scrape (Anda harus mengetik URL ini secara manual karena tidak ada di navigasi umum).
Login dengan akun yang sudah Anda buat (jika belum punya, daftar dulu di /register).
Klik tombol "Jalankan Scraping Sekarang". Proses ini akan memakan waktu. Amati terminal untuk melihat progress-nya.
Setelah selesai, Anda akan melihat notifikasi "Scraping berhasil!"

7. Nikmati Website Anda!
Sekarang, kembali ke halaman utama http://127.0.0.1:5000/. Anda akan melihat:

Banner Anda tampil dan bisa di-scroll.
Produk-produk dengan gambar, harga (asli & diskon), merek, dan rating.
Pagination berfungsi di bagian bawah.
Fitur pencarian, detail produk, dan komentar semuanya aktif.
Selamat Mencoba! 🚀
