from flask import render_template, jsonify, request, current_app, send_file, abort, flash, redirect, url_for, session
from flask_login import current_user, login_required
from app.main import bp
from app import db
from app.models import Project, MusicFile
from app.music_engine import MusicGenerator, AudioConverter, ChordProcessor
from flask_babel import _
from datetime import datetime
import os
import json

# 初始化音樂生成器
music_generator = MusicGenerator()
audio_converter = AudioConverter()
chord_processor = ChordProcessor()

@bp.route('/')
@bp.route('/index')
def index():
    """首頁"""
    if current_user.is_authenticated:
        recent_projects = Project.query.filter_by(user_id=current_user.id)\
            .order_by(Project.created_at.desc())\
            .limit(4).all()
        all_projects = Project.query.filter_by(user_id=current_user.id)\
            .order_by(Project.created_at.desc()).all()
    else:
        recent_projects = []
        all_projects = []
    
    return render_template('main/index.html',
                         title=_('AI Music Creator'),
                         recent_projects=recent_projects,
                         all_projects=all_projects,
                         show_previous_works=True)

@bp.route('/create_music', methods=['POST'])
@login_required
def create_music():
    """創建音樂"""
    # 獲取參數
    mode = request.form.get('mode', 'simple')
    style = request.form.get('style', 'pop')
    mood = request.form.get('mood', 'happy')
    duration = float(request.form.get('duration', 60))
    tempo = int(request.form.get('tempo', 120))
    chord_progression = request.form.get('chord_progression', '')
    
    # 驗證參數
    if duration <= 0 or duration > current_app.config['MAX_DURATION']:
        return jsonify({
            'status': 'error',
            'message': _('Duration must be between 0 and %(max)d seconds', max=current_app.config['MAX_DURATION'])
        }), 400
    
    # 生成音樂
    result = music_generator.generate_music({
        'mode': mode,
        'style': style,
        'mood': mood,
        'duration': duration,
        'tempo': tempo,
        'chord_progression': chord_progression
    })
    
    if result['status'] == 'success':
        # 創建新項目
        project = Project(
            user_id=current_user.id,
            title=f"Project {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            style=style,
            mood=mood,
            tempo=tempo,
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
        return jsonify({
            'status': 'error',
            'message': result['message']
        }), 500

@bp.route('/projects')
@login_required
def projects():
    """項目列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    projects = Project.query.filter_by(user_id=current_user.id)\
        .order_by(Project.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/projects.html',
                         title=_('My Projects'),
                         projects=projects)

@bp.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    """项目详情页面"""
    project = Project.query.get_or_404(project_id)
    
    # 检查权限
    if project.user_id != current_user.id and not project.is_public:
        abort(403)
    
    return render_template('main/project_detail.html',
                         title=project.title,
                         project=project)

@bp.route('/project/<int:project_id>/download')
@login_required
def download_project(project_id):
    """下载项目文件"""
    project = Project.query.get_or_404(project_id)
    
    # 检查权限
    if project.user_id != current_user.id and not project.is_public:
        abort(403)
    
    # 获取文件路径
    file_path = os.path.join(current_app.static_folder, project.audio_path)
    
    return send_file(file_path,
                    as_attachment=True,
                    download_name=f"{project.title}.mp3")

@bp.route('/project/<int:project_id>/delete', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """删除项目"""
    project = Project.query.get_or_404(project_id)
    
    # 检查权限
    if project.user_id != current_user.id:
        return jsonify({
            'status': 'error',
            'message': _('Permission denied')
        }), 403
    
    try:
        # 删除相关文件
        if project.audio_path:
            audio_file = os.path.join(current_app.static_folder, project.audio_path)
            if os.path.exists(audio_file):
                os.remove(audio_file)
        
        if project.midi_path:
            midi_file = os.path.join(current_app.static_folder, project.midi_path)
            if os.path.exists(midi_file):
                os.remove(midi_file)
        
        # 从数据库中删除
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': _('Project deleted successfully')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/project/<int:project_id>/export')
@login_required
def export_project(project_id):
    """导出项目"""
    project = Project.query.get_or_404(project_id)
    
    # 检查权限
    if project.user_id != current_user.id and not project.is_public:
        abort(403)
    
    format = request.args.get('format', 'mp3')
    if format not in ['midi', 'mp3', 'wav']:
        abort(400)
    
    try:
        if format == 'midi':
            # 确保midi_path存在
            if not project.midi_path:
                return jsonify({
                    'status': 'error',
                    'message': _('MIDI file not available for this project')
                }), 404
                
            file_path = os.path.join(current_app.static_folder, project.midi_path)
            if not os.path.exists(file_path):
                # 如果MIDI文件不存在，尝试重新创建
                current_app.logger.warning(f"MIDI file not found: {file_path}, attempting to recreate")
                # 这里可以添加重新创建MIDI文件的逻辑
                return jsonify({
                    'status': 'error',
                    'message': _('MIDI file not found, please regenerate the music')
                }), 404
            
            filename = f"{project.title}.mid"
        else:
            if not project.audio_path:
                return jsonify({
                    'status': 'error',
                    'message': _('Audio file not available for this project')
                }), 404
                
            file_path = os.path.join(current_app.static_folder, project.audio_path)
            if not os.path.exists(file_path):
                return jsonify({
                    'status': 'error',
                    'message': _('Audio file not found, please regenerate the music')
                }), 404
                
            filename = f"{project.title}.{format}"
        
        # 记录导出日志
        current_app.logger.info(f"Exporting project {project_id} as {format}: {file_path}")
        
        return send_file(file_path,
                        as_attachment=True,
                        download_name=filename)
    except Exception as e:
        current_app.logger.error(f"Export error for project {project_id}: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/project/<int:project_id>/visibility', methods=['POST'])
@login_required
def toggle_project_visibility(project_id):
    """切换项目可见性"""
    project = Project.query.get_or_404(project_id)
    
    # 检查权限
    if project.user_id != current_user.id:
        return jsonify({
            'status': 'error',
            'message': _('Permission denied')
        }), 403
    
    try:
        data = request.get_json()
        project.is_public = data.get('is_public', False)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': _('Project visibility updated')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/project/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def project_edit(id):
    """编辑项目"""
    project = Project.query.get_or_404(id)
    
    # 检查权限
    if project.user_id != current_user.id:
        return jsonify({
            'status': 'error',
            'message': _('Permission denied')
        }), 403
    
    if request.method == 'POST':
        try:
            # 更新项目信息
            project.title = request.form.get('title', project.title)
            project.style = request.form.get('style', project.style)
            project.description = request.form.get('description', project.description)
            project.is_public = request.form.get('is_public') == '1'
            
            # 保存更改
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': _('Project updated successfully')
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    return render_template('main/project_edit.html',
                         title=_('Edit Project'),
                         project=project)

@bp.route('/get_chord_suggestions')
@login_required
def get_chord_suggestions():
    """獲取和弦建議"""
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

@bp.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        title = request.form.get('name')
        description = request.form.get('description')
        
        if not title:
            flash('項目名稱不能為空', 'error')
            return redirect(url_for('main.create_project'))
        
        project = Project(title=title, description=description, user_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        
        flash('項目創建成功', 'success')
        return redirect(url_for('main.project_detail', project_id=project.id))
    
    return render_template('main/create_project.html',
                         title='創建新項目')

@bp.route('/generate_music', methods=['POST'])
@login_required
def generate_music():
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        prompt = data.get('prompt')
        duration = int(data.get('duration', 30))
        temperature = float(data.get('temperature', 0.8))
        
        if not prompt:
            return jsonify({'error': '請輸入提示詞'}), 400
        
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            return jsonify({'error': '您沒有權限在此項目中生成音樂'}), 403
        
        # 生成音樂
        generator = MusicGenerator()
        result = generator.generate_music({
            'style': 'pop',
            'mood': 'happy',
            'duration': duration,
            'tempo': 120
        })
        
        if result['status'] != 'success':
            return jsonify({'error': result.get('message', '生成音樂時發生錯誤')}), 500
        
        # 保存音樂文件
        music_file = MusicFile(
            project_id=project_id,
            prompt=prompt,
            file_path=result['audio_path'],
            duration=duration,
            temperature=temperature
        )
        db.session.add(music_file)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'file_url': url_for('static', filename=result['audio_path']),
            'music_id': music_file.id
        })
        
    except Exception as e:
        current_app.logger.error(f'生成音樂時發生錯誤: {str(e)}')
        return jsonify({'error': '生成音樂時發生錯誤'}), 500

@bp.route('/delete_music/<int:music_id>', methods=['POST'])
@login_required
def delete_music(music_id):
    music = MusicFile.query.get_or_404(music_id)
    project = Project.query.get(music.project_id)
    
    if not project or project.user_id != current_user.id:
        return jsonify({'error': '您沒有權限刪除此音樂'}), 403
    
    try:
        # 刪除文件
        file_path = os.path.join(current_app.static_folder, music.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 刪除數據庫記錄
        db.session.delete(music)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f'刪除音樂時發生錯誤: {str(e)}')
        return jsonify({'error': '刪除音樂時發生錯誤'}), 500

@bp.route('/language_test')
def language_test():
    """测试语言功能的页面"""
    return render_template('main/language_test.html', title="语言测试")

@bp.route('/session_tools')
def session_tools():
    """会话工具页面"""
    return render_template('main/session_tools.html', 
                          title="会话工具", 
                          session_data=dict(session))

@bp.route('/session_set/<key>/<value>')
def session_set(key, value):
    """直接设置会话变量"""
    session[key] = value
    session.modified = True
    current_app.logger.info(f"直接设置会话: {key} = {value}")
    current_app.logger.info(f"会话内容: {dict(session)}")
    return redirect(url_for('main.session_tools'))

@bp.route('/session_clear')
def session_clear():
    """清空会话"""
    session.clear()
    current_app.logger.info("已清空会话")
    return redirect(url_for('main.session_tools')) 