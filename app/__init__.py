from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_caching import Cache
from flask_recaptcha import ReCaptcha
from flask_babel import Babel, lazy_gettext as _l
from markupsafe import Markup
from config import config
import os

# 初始化擴展
db = SQLAlchemy()
login = LoginManager()
migrate = Migrate()
cache = Cache()
recaptcha = ReCaptcha()
babel = Babel()

# Monkey patch Flask-ReCAPTCHA
import flask_recaptcha
flask_recaptcha.Markup = Markup

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 设置会话配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1小时
    
    # 初始化擴展
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    recaptcha.init_app(app)
    
    # 设置语言本地化
    def get_locale():
        # 从用户会话中获取语言设置
        if 'language' in session:
            return session['language']
        # 或从请求头中获取
        return request.accept_languages.best_match(app.config['LANGUAGES'])
    
    babel.init_app(app, locale_selector=get_locale)
    
    # 设置翻译函数为全局可用
    from flask_babel import _
    app.jinja_env.globals['_'] = _
    
    # 設置登錄視圖
    login.login_view = 'auth.login'
    login.login_message = '請先登錄以訪問此頁面。'
    
    # 註冊藍圖
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 創建數據庫表
    with app.app_context():
        db.create_all()
    
    # 将LANGUAGE_NAMES添加到模板全局变量
    @app.context_processor
    def inject_language_names():
        return dict(
            LANGUAGES=app.config['LANGUAGES'],
            LANGUAGE_NAMES=app.config['LANGUAGE_NAMES']
        )
    
    return app 