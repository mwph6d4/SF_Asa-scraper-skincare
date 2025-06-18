# app.py
from flask import Flask
from config import Config
import os

from extensions import db, login_manager
from flask_migrate import Migrate  # ✅ Tambahkan ini

app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi ekstensi
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Impor model setelah db diinisialisasi
from models import User, Product, Comment, History

# Inisialisasi Flask-Migrate
migrate = Migrate(app, db)  # ✅ Inisialisasi Flask-Migrate

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Impor routes terakhir
from routes import *

# Buat database jika belum ada
with app.app_context():
    db.create_all()
    print("Database created or already exists!")

if __name__ == '__main__':
    app.run(debug=True)
