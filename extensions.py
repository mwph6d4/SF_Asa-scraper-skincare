# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inisialisasi ekstensi tanpa mengikatnya ke aplikasi Flask di sini
# Mereka akan diinisialisasi dengan aplikasi di app.py
db = SQLAlchemy()
login_manager = LoginManager()