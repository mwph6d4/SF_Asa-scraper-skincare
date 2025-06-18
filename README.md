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
