from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    history = db.relationship('History', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_price = db.Column(db.String(100), nullable=True)  # Harga setelah diskon
    source_website = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Float, nullable=True)

    original_price = db.Column(db.String(100), nullable=True)  # Harga asli/sebelum diskon
    saved_amount = db.Column(db.String(100), nullable=True)    # Jumlah yang dihemat
    description = db.Column(db.Text, nullable=True)            # Deskripsi produk

    usage_instructions = db.Column(db.Text, nullable=True)     # Cara penggunaan
    ingredients = db.Column(db.Text, nullable=True)            # Komposisi bahan

    # Relasi
    product_comments = db.relationship('Comment', backref='product', lazy='dynamic')
    product_history_entries = db.relationship('History', backref='product_scraped', lazy='dynamic')

    def __repr__(self):
        return f'<Product {self.product_name} from {self.source_website} ({self.brand})>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id} on Product {self.product_id}>'

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    scraped_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<History {self.id} User: {self.user_id} @ {self.scraped_at}>'

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_name = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Settings {self.setting_name}: {self.setting_value}>'

# --- TAMBAHKAN KELAS BANNER INI DI BAWAH ---
class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    link_url = db.Column(db.String(500), nullable=True) # URL yang dikunjungi saat banner diklik
    order_num = db.Column(db.Integer, default=0) # Untuk urutan banner jika diperlukan
    
    def __repr__(self):
        return f'<Banner {self.id}: {self.image_url}>'