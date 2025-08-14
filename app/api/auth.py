from flask_httpauth import HTTPTokenAuth
from app.models import User
from app.api.errors import error_response

token_auth = HTTPTokenAuth()

@token_auth.verify_token
def verify_token(token):
    """驗證令牌"""
    return User.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error():
    """認證錯誤處理"""
    return error_response(401) 