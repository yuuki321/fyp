from flask import render_template, jsonify, request, redirect, url_for, flash, send_file
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.models import User, Project
from app.forms import LoginForm, RegistrationForm
from flask_babel import _
from datetime import datetime
from urllib.parse import urlparse
from app.music_engine import MusicGenerator, AudioConverter, ChordProcessor
import os

# 初始化音樂生成器
music_generator = MusicGenerator()
audio_converter = AudioConverter()
chord_processor = ChordProcessor()

@app.route('/')
def index():
    if current_user.is_authenticated:
        recent_projects = Project.query.filter_by(user_id=current_user.id)\
            .order_by(Project.created_at.desc())\
            .limit(4).all()
        all_projects = Project.query.filter_by(user_id=current_user.id)\
            .order_by(Project.created_at.desc()).all()
    else:
        recent_projects = []
        all_projects = []
    return render_template('index.html', 
                         title=_('AI Music Creator'),
                         recent_projects=recent_projects,
                         all_projects=all_projects,
                         show_previous_works=True)

@app.route('/create_music', methods=['POST'])
@login_required
def create_music():
    try:
        # 获取参数
        mode = request.form.get('mode', 'simple')
        style = request.form.get('style', 'pop')
        mood = request.form.get('mood', 'happy')
        duration = float(request.form.get('duration', 60))
        tempo = int(request.form.get('tempo', 120))
        chord_progression = request.form.get('chord_progression', '')
        
        # 记录请求参数
        app.logger.debug(f"Received music generation request: {request.form}")
        
        # 验证参数
        if duration <= 0 or duration > 300:
            return jsonify({
                'status': 'error',
                'message': _('Duration must be between 0 and 300 seconds')
            }), 400
            
        # 生成音乐
        result = music_generator.generate_music({
            'mode': mode,
            'style': style,
            'mood': mood,
            'duration': duration,
            'tempo': tempo,
            'chord_progression': chord_progression
        })
        
        app.logger.debug(f"Music generation result: {result}")
        
        if result['status'] == 'success':
            # 创建新项目
            project = Project(
                user_id=current_user.id,
                title=f"Project {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                style=style,
                duration=duration,
                chord_progression=chord_progression,
                midi_path=result['midi_path'],
                audio_path=result['audio_path']
            )
            db.session.add(project)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'project_id': project.id,
                'message': _('Music created successfully')
            })
        else:
            app.logger.error(f"Music generation failed: {result['message']}")
            return jsonify({
                'status': 'error',
                'message': result['message']
            }), 500
            
    except Exception as e:
        app.logger.error(f"Error in create_music: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/get_chord_suggestions', methods=['GET'])
@login_required
def get_chord_suggestions():
    style = request.args.get('style', 'pop')
    key = request.args.get('key', 'C')
    current_chord = request.args.get('current_chord')
    
    if current_chord:
        suggestions = chord_processor.suggest_next_chord(current_chord, style)
    else:
        suggestions = chord_processor.get_progression(style, key)
    
    return jsonify({
        'status': 'success',
        'suggestions': suggestions
    })

@app.route('/upload_track', methods=['POST'])
@login_required
def upload_track():
    if 'file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': _('No file uploaded')
        }), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': _('No file selected')
        }), 400
        
    if file:
        # 保存上傳的文件
        filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(file.filename)[1]}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 根據文件類型進行處理
        if file.filename.endswith('.mid') or file.filename.endswith('.midi'):
            # 處理MIDI文件
            result = music_generator.complete_track(file_path, {
                'style': request.form.get('style', 'pop'),
                'duration': float(request.form.get('duration', 60))
            })
        else:
            # 處理音頻文件
            # 先轉換為WAV格式
            wav_path = audio_converter.convert_to_wav(file_path)
            # TODO: 實現音頻補全邏輯
            result = {
                'status': 'success',
                'audio_path': wav_path
            }
            
        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'message': _('File processed successfully'),
                'audio_path': result.get('audio_path')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            }), 500
            
    return jsonify({
        'status': 'error',
        'message': _('File processing failed')
    }), 500

@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    """下載生成的文件"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404

@app.route('/previous_works')
@login_required
def previous_works():
    # 獲取用戶所有作品，按創建時間排序
    projects = Project.query.filter_by(user_id=current_user.id)\
        .order_by(Project.created_at.desc()).all()
    return render_template('previous_works.html', 
                         title=_('Previous Works'),
                         projects=projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(f"Login attempt - Username: {form.username.data}")  # 调试信息
        
        if user is None:
            print("User not found")  # 调试信息
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
            
        if not user.check_password(form.password.data):
            print("Invalid password")  # 调试信息
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
            
        print(f"Successful login for user: {user.username}")  # 调试信息
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 获取下一页的URL
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
            
        return redirect(next_page)
        
    return render_template('login.html', title=_('Sign In'), form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title=_('User Profile'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin():
        flash(_('Access denied. Admin privileges required.'))
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin.html', title=_('Admin Panel'), users=users)

@app.route('/admin/user/<int:user_id>/role', methods=['POST'])
@login_required
def update_user_role(user_id):
    if not current_user.is_admin():
        return jsonify({'status': 'error', 'message': _('Access denied')}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in ['user', 'premium', 'admin']:
        return jsonify({'status': 'error', 'message': _('Invalid role')}), 400
    
    user.role = new_role
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        return jsonify({'status': 'error', 'message': _('Access denied')}), 403
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'status': 'error', 'message': _('Cannot delete yourself')}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin/model/add', methods=['POST'])
@login_required
def add_model():
    if not current_user.is_admin():
        return jsonify({'status': 'error', 'message': _('Access denied')}), 403
    
    # 这里添加模型的逻辑
    return jsonify({'status': 'success'})

@app.route('/admin/model/<int:model_id>/toggle', methods=['POST'])
@login_required
def toggle_model(model_id):
    if not current_user.is_admin():
        return jsonify({'status': 'error', 'message': _('Access denied')}), 403
    
    # 这里切换模型状态的逻辑
    return jsonify({'status': 'success'})

@app.route('/admin/model/train', methods=['POST'])
@login_required
def train_model():
    if not current_user.is_admin():
        return jsonify({'status': 'error', 'message': _('Access denied')}), 403
    
    # 这里添加模型训练的逻辑
    return jsonify({
        'status': 'success',
        'training_id': 'some-training-id'  # 实际应用中需要生成真实的训练ID
    })

@app.route('/admin/training/<training_id>/status')
@login_required
def training_status(training_id):
    if not current_user.is_admin():
        return jsonify({'status': 'error', 'message': _('Access denied')}), 403
    
    # 这里获取训练状态的逻辑
    return jsonify({
        'progress': 50,  # 示例进度
        'status': _('Training in progress...')
    })

@app.route('/project/<int:project_id>')
@login_required
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403
    return jsonify(project.to_dict())

@app.route('/project/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Access denied'}), 403
    db.session.delete(project)
    db.session.commit()
    return jsonify({'status': 'success'}) 