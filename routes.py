# routes.py
from flask import render_template, url_for, flash, redirect, request
from app import app
from extensions import db, login_manager

# Impor model yang dibutuhkan
from models import User, Product, Comment, History, Settings, Banner
# Kita perlu FlaskForm untuk form login/register
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# --- PENTING: Impor HANYA scrape_sociolla, scrape_main_banner_sociolla TIDAK DIPERLUKAN LAGI ---
from scrape import scrape_sociolla


# --- Definisi Form (Disarankan dipindahkan ke forms.py) ---
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username sudah ada. Silakan pilih username lain.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Ingat Saya')
    submit = SubmitField('Login')
# --- Akhir Definisi Form ---


# --- ROUTE UTAMA (MENAMPILKAN PRODUK DENGAN PAGINATION DAN BANNER LOKAL) ---
@app.route('/')
@app.route('/home')
@app.route('/products')
@app.route('/products/<int:page>')
def home(page=1):
    per_page = 20
    products_paginated = Product.query.filter(
        Product.product_name != 'Pretty Things For You'
    ).order_by(Product.id.asc()).paginate(page=page, per_page=per_page, error_out=False)

    # --- PENTING: Ambil Semua Banner LOKAL dari Database ---
    banners = Banner.query.order_by(Banner.order_num.asc()).all()
    # --------------------------------------------------

    return render_template('index.html',
                           products_paginated=products_paginated,
                           title='Semua Produk',
                           banners=banners)

# --- ROUTE LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Login berhasil!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login gagal. Periksa username dan password', 'danger')
    return render_template('login.html', title='Login', form=form)

# --- ROUTE REGISTRASI ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Akun Anda telah dibuat! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# --- ROUTE LOGOUT ---
@app.route('/logout')
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('home'))

# --- ROUTE UNTUK SCRAPING ---
@app.route('/run_scrape', methods=['GET', 'POST'])
@login_required
def run_scrape():
    if request.method == 'POST':
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options

        chromedriver_path = r'C:\Users\DELL\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--headless') # Komen ini untuk debugging visual
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')

        service = Service(executable_path=chromedriver_path)
        service.start_session_timeout = 180

        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            # --- BAGIAN BARU: SIMPAN BANNER LOKAL KE DATABASE ---
            print("\n--- Starting Local Banner Storage ---")
            # Daftar URL banner lokal Anda
            local_banner_urls = [
                url_for('static', filename='images/banner1.jpg'), # URL untuk banner1.jpg
                url_for('static', filename='images/banner2.jpg')  # URL untuk banner2.jpg
                # Tambahkan lebih banyak jika ada banner lain
            ]

            with app.app_context():
                # Hapus semua banner lama dari tabel Banner sebelum menyimpan yang baru
                db.session.query(Banner).delete()
                db.session.commit() # Commit penghapusan

                for i, banner_file_url in enumerate(local_banner_urls):
                    new_banner = Banner(
                        image_url=banner_file_url,
                        link_url="#", # Link default jika tidak ada link spesifik untuk banner ini
                        order_num=i
                    )
                    db.session.add(new_banner)
                db.session.commit() # Commit semua banner baru
                print(f"Successfully committed {len(local_banner_urls)} local banners to database.")
            print("--- Finished Local Banner Storage ---\n")
            # --- AKHIR BAGIAN BARU ---

            # ... (seluruh kode scraping produk tetap sama seperti versi terakhir) ...
            search_keywords_for_sociolla = [
                'wardah', 'somethinc', 'azarine', 'loreal paris', 'maybelline'
            ]
            all_combined_products_across_searches = []

            for keyword in search_keywords_for_sociolla:
                product_data_from_sociolla = scrape_sociolla(driver, keyword)
                all_combined_products_across_searches.extend(product_data_from_sociolla)

            print(f"\n--- Scraping Summary ---")
            print(f"Total items scraped from all searches: {len(all_combined_products_across_searches)}")

            if not all_combined_products_across_searches:
                print("No products were successfully scraped. Database will remain empty.")
                flash('Scraping selesai, tetapi tidak ada produk yang berhasil di-scrape.', 'info')
                return render_template('scrape_page.html', title='Jalankan Scraping')

            new_products_count = 0
            for item in all_combined_products_across_searches:
                existing_product = Product.query.filter_by(
                    product_name=item['product_name'],
                    source_website=item['source_website'],
                    brand=item['brand']
                ).first()

                # Fungsi helper untuk mengubah string kosong atau None menjadi None yang sebenarnya
                def get_clean_text(value):
                    if value is None or (isinstance(value, str) and value.strip() == ''):
                        return None
                    return value

                item_description = get_clean_text(item.get('description'))
                item_how_to_use = get_clean_text(item.get('how_to_use'))
                item_ingredients = get_clean_text(item.get('ingredients'))


                if not existing_product:
                    new_product = Product(
                        product_name=item['product_name'],
                        product_price=item['product_price'],
                        source_website=item['source_website'],
                        brand=item['brand'],
                        image_url=item['image_url'],
                        rating=item['rating'],
                        original_price=item['original_price'],
                        saved_amount=item['saved_amount'],
                        description=item_description, # Gunakan nilai yang sudah dibersihkan
                        usage_instructions=item_how_to_use, # Gunakan nilai yang sudah dibersihkan
                        ingredients=item_ingredients # Gunakan nilai yang sudah dibersihkan
                    )
                    db.session.add(new_product)
                    new_products_count += 1
                else:
                    # Update existing product if found
                    existing_product.product_price = item['product_price']
                    existing_product.image_url = item['image_url']
                    existing_product.rating = item['rating']
                    existing_product.original_price = item['original_price']
                    existing_product.saved_amount = item['saved_amount']
                    existing_product.description = item_description
                    existing_product.usage_instructions = item_how_to_use
                    existing_product.ingredients = item_ingredients
                    print(f"  Produk '{item['product_name']}' sudah ada, diupdate.")


            try:
                db.session.commit() # Commit produk
                print(f"Successfully committed {new_products_count} new products to database.")

                history_entry = History(
                    user_id=current_user.id,
                    scraped_at=datetime.utcnow(),
                    product_id=None # Ini adalah entri untuk aktivitas scraping umum
                )
                db.session.add(history_entry)
                db.session.commit() # Commit history
                print("History entry committed.")

                flash(f'Scraping berhasil! {new_products_count} produk baru ditambahkan/diupdate. Riwayat scraping dicatat.', 'success')

            except Exception as commit_error:
                db.session.rollback()
                print(f"!!! DATABASE COMMIT FAILED: {commit_error}")
                flash(f'Scraping berhasil, tetapi gagal menyimpan data ke database: {commit_error}', 'danger')


        except Exception as main_scrape_error:
            print(f"!!! MAIN SCRAPE PROCESS FAILED: {main_scrape_error}")
            db.session.rollback()
            flash(f'Scraping gagal total: {main_scrape_error}', 'danger')

        finally:
            driver.quit()
            print("Selenium driver quit.")

    return render_template('scrape_page.html', title='Jalankan Scraping')

# --- ROUTE PROFIL PENGGUNA ---
@app.route('/profile')
@login_required
def profile():
    # Mengambil riwayat tampilan produk
    # Memfilter entri History di mana product_id TIDAK NULL
    # dan mengurutkan berdasarkan waktu tampilan terbaru
    product_view_history = History.query.filter_by(user_id=current_user.id).filter(History.product_id.isnot(None)).order_by(History.scraped_at.desc()).all()

    # (Opsional) Jika Anda masih ingin menampilkan riwayat scraping umum, Anda bisa mengambilnya secara terpisah:
    # general_scrape_history = History.query.filter_by(user_id=current_user.id, product_id=None).order_by(History.scraped_at.desc()).all()

    return render_template('profile.html',
                           title='Profil Pengguna',
                           product_view_history=product_view_history)
                           # general_scrape_history=general_scrape_history) # Jika ingin menampilkan keduanya

# --- ROUTE DETAIL PRODUK DAN KOMENTAR ---
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    comments = Comment.query.filter_by(product_id=product.id).order_by(Comment.timestamp.desc()).all()

    # --- BAGIAN BARU: CATAT RIWAYAT TAMPILAN PRODUK ---
    if current_user.is_authenticated: # Hanya catat jika pengguna login
        # Periksa apakah entri histori sudah ada dalam 5 menit terakhir untuk produk ini
        # Ini untuk menghindari pencatatan berlebihan jika user refresh halaman
        recent_history = History.query.filter_by(
            user_id=current_user.id,
            product_id=product.id
        ).filter(
            History.scraped_at > (datetime.utcnow() - timedelta(minutes=5))
        ).first()

        if not recent_history:
            new_view_history = History(
                user_id=current_user.id,
                product_id=product.id, # Sekarang product_id akan terisi
                scraped_at=datetime.utcnow() # Timestamp tampilan
            )
            db.session.add(new_view_history)
            try:
                db.session.commit()
                print(f"User {current_user.username} viewed product {product.product_name}. History recorded.")
            except Exception as e:
                db.session.rollback()
                print(f"Failed to record product view history: {e}")
    # --- AKHIR BAGIAN BARU ---

    return render_template('product_detail.html', title=product.product_name, product=product, comments=comments)

@app.route('/product/<int:product_id>/comment', methods=['POST'])
@login_required
def add_comment(product_id):
    product = Product.query.get_or_404(product_id)
    comment_text = request.form.get('comment_text')
    if comment_text:
        new_comment = Comment(
            user_id=current_user.id,
            product_id=product.id,
            comment_text=comment_text
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('Komentar berhasil ditambahkan!', 'success')
    else:
        flash('Komentar tidak boleh kosong.', 'danger')
    return redirect(url_for('product_detail', product_id=product.id))

# --- ROUTE PENCARIAN ---
@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    products = []
    if keyword:
        products = Product.query.filter(
            Product.product_name != 'Pretty Things For You',
            Product.product_name.ilike(f'%{keyword}%')
        ).all()
        if not products:
            flash(f"Tidak ditemukan produk dengan keyword '{keyword}'.", 'info')
    else:
        flash("Masukkan keyword pencarian.", 'info')

    return render_template('search_results.html', title='Hasil Pencarian', products=products, keyword=keyword)

# --- ROUTE PERBANDINGAN PRODUK BARU ---
@app.route('/compare')
def compare_products():
    product_ids_str = request.args.get('ids', '')
    product_ids = [int(p_id) for p_id in product_ids_str.split(',') if p_id.isdigit()]

    # Ambil produk dari database berdasarkan ID
    products = Product.query.filter(Product.id.in_(product_ids)).all()

    # Urutkan produk sesuai urutan ID yang diminta (opsional, tapi bagus untuk konsistensi)
    # Membuat dictionary untuk akses cepat
    products_dict = {product.id: product for product in products}
    # Membuat list produk sesuai urutan id yang diterima dari URL
    ordered_products = [products_dict[p_id] for p_id in product_ids if p_id in products_dict]


    return render_template('compare.html', title='Bandingkan Produk', products=ordered_products)