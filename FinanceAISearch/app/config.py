import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SERPER_API_KEY = os.environ.get('SERPER_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    # # Sql
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '../instance', 'users.db')
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'  # 本地SQLite数据库文件
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 云端 MySQL 数据库配置
    # SQLALCHEMY_DATABASE_URI = ''
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    # CORS配置
    CORS_ORIGINS = [
        'https://finaisearch.com',
        'http://localhost:5173',
        'http://localhost:8000',
        'http://localhost:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:3000'
        'http://127.0.0.1:4000'
        'http://127.0.0.1:8000'
    ]
