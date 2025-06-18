import os

class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci-rahasia-anda-yang-unik-dan-sulit-ditebak-disini'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False