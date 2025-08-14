from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, current_user
from app import db, recaptcha
from app.auth import bp
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_babel import _
from datetime import datetime

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """用戶登錄"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title=_('Sign In'), form=form)

@bp.route('/logout')
def logout():
    """用戶登出"""
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """用戶註冊"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # 移除reCAPTCHA验证
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'), 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title=_('Register'), form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """請求重置密碼"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # TODO: 發送密碼重置郵件
            flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html',
                         title=_('Reset Password'),
                         form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密碼"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html',
                         title=_('Reset Password'),
                         form=form)

@bp.route('/change_password', methods=['POST'])
def change_password():
    """修改密碼"""
    if not current_user.is_authenticated:
        return jsonify({'status': 'error', 'message': _('Please login first')}), 401
    
    data = request.get_json()
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({'status': 'error', 'message': _('Invalid request')}), 400
    
    if not current_user.check_password(data['old_password']):
        return jsonify({'status': 'error', 'message': _('Invalid old password')}), 400
    
    current_user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': _('Password updated successfully')})

@bp.route('/change_language', methods=['POST'])
def change_language():
    """切换语言"""
    data = request.get_json()
    if not data or 'language' not in data:
        return jsonify({'status': 'error', 'message': _('Invalid request')}), 400
    
    language = data['language']
    
    # 检查语言是否受支持
    from flask import current_app
    if language not in current_app.config['LANGUAGES']:
        return jsonify({'status': 'error', 'message': _('Unsupported language')}), 400
    
    # 保存到session中
    session['language'] = language
    
    return jsonify({
        'status': 'success', 
        'message': _('Language changed successfully'),
        'language': language
    }) 