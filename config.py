import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

class Config:
    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    DEBUG = True
    TESTING = False
    
    # 數據庫配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上傳配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'mid', 'midi', 'mp3', 'wav'}
    
    # 多語言支持
    LANGUAGES = ['en', 'zh_TW', 'zh_CN']
    LANGUAGE_NAMES = {
        'en': 'English',
        'zh_TW': '繁體中文',
        'zh_CN': '简体中文'
    }
    BABEL_DEFAULT_LOCALE = 'zh_TW'
    BABEL_SUPPORTED_LOCALES = ['en', 'zh_TW', 'zh_CN']
    
    # 會話配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    
    # 音樂生成配置
    MAX_DURATION = 300  # 最大音樂時長（秒）
    MIN_DURATION = 10   # 最小音樂時長（秒）
    DEFAULT_TEMPO = 120 # 預設速度（BPM）
    MIN_TEMPO = 60      # 最小速度（BPM）
    MAX_TEMPO = 240     # 最大速度（BPM）
    
    # 和弦配置
    CHORD_TYPES = {
        'maj': '大三和弦',
        'min': '小三和弦',
        'dim': '減三和弦',
        'aug': '增三和弦',
        'maj7': '大七和弦',
        'min7': '小七和弦',
        'dom7': '屬七和弦',
        'dim7': '減七和弦',
        'maj9': '大九和弦',
        'min9': '小九和弦',
        'sus2': '掛留二和弦',
        'sus4': '掛留四和弦',
        'add9': '加九和弦',
        'maj6': '大六和弦',
        'min6': '小六和弦',
        'm7b5': '半減七和弦',
        'aug7': '增七和弦',
        '7sus4': '掛留四屬七和弦',
        '9sus4': '掛留四九和弦',
        'add11': '加十一和弦',
        'maj13': '大十三和弦',
        'min11': '小十一和弦',
        '13': '十三和弦',
        '7b9': '變九和弦',
        '7#9': '升九和弦'
    }
    
    # 情緒配置
    MOODS = {
        'happy': '快樂',
        'sad': '悲傷',
        'energetic': '活力',
        'calm': '平靜',
        'romantic': '浪漫',
        'mysterious': '神秘',
        'dramatic': '戲劇性',
        'peaceful': '平和',
        'nostalgic': '懷舊',
        'dreamy': '夢幻',
        'passionate': '熱情',
        'melancholic': '憂鬱',
        'epic': '壯麗',
        'playful': '俏皮',
        'dark': '陰暗',
        'hopeful': '充滿希望',
        'tense': '緊張',
        'ethereal': '空靈',
        'whimsical': '異想天開',
        'aggressive': '激進',
        'triumphant': '勝利的',
        'majestic': '莊嚴的'
    }
    
    # 主題配置
    THEMES = {
        'light': '淺色模式',
        'dark': '深色模式'
    }
    
    # 驗證碼配置
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
    RECAPTCHA_USE_SSL = True
    RECAPTCHA_OPTIONS = {
        'theme': 'light', 
        'size': 'normal',
        'hl': 'zh-CN'  # 默认中文语言，用户可通过界面切换
    }
    
    # AI模型配置
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    DEFAULT_MODEL = 'base_model.h5'
    
    # 緩存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # API限制
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # 安全配置
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    @staticmethod
    def init_app(app):
        # 創建必要的目錄
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.MODEL_PATH, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False
    RECAPTCHA_PUBLIC_KEY = 'test'
    RECAPTCHA_PRIVATE_KEY = 'test'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:pass@localhost/dbname'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 生產環境特定的配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        # 設置日誌
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log',
                                         maxBytes=10240,
                                         backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 