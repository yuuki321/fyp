from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User
from flask_babel import lazy_gettext as _l
from flask_recaptcha import ReCaptcha

class LoginForm(FlaskForm):
    """登錄表單"""
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
    """註冊表單"""
    username = StringField(_l('Username'), validators=[
        DataRequired(),
        Length(min=3, max=64)
    ])
    email = StringField(_l('Email'), validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    password = PasswordField(_l('Password'), validators=[
        DataRequired(),
        Length(min=8, message=_l('Password must be at least 8 characters long'))
    ])
    password2 = PasswordField(_l('Confirm Password'), validators=[
        DataRequired(),
        EqualTo('password', message=_l('Passwords must match'))
    ])
    submit = SubmitField(_l('Register'))
    
    def validate_username(self, username):
        """驗證用戶名是否已存在"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))
    
    def validate_email(self, email):
        """驗證郵箱是否已存在"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different email address.'))

class ResetPasswordRequestForm(FlaskForm):
    """請求重置密碼表單"""
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    """重置密碼表單"""
    password = PasswordField(_l('New Password'), validators=[
        DataRequired(),
        Length(min=8, message=_l('Password must be at least 8 characters long'))
    ])
    password2 = PasswordField(_l('Confirm Password'), validators=[
        DataRequired(),
        EqualTo('password', message=_l('Passwords must match'))
    ])
    submit = SubmitField(_l('Reset Password')) 