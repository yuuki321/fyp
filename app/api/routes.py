from flask import jsonify, request, current_app, url_for
from app import db
from app.api import bp
from app.models import User, Project
from app.api.auth import token_auth
from app.api.errors import bad_request, error_response
from flask_babel import _

@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    """獲取用戶信息"""
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())

@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    """獲取用戶列表"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)

@bp.route('/projects', methods=['GET'])
@token_auth.login_required
def get_projects():
    """獲取項目列表"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    query = Project.query.filter_by(user_id=token_auth.current_user().id)
    data = Project.to_collection_dict(query, page, per_page, 'api.get_projects')
    return jsonify(data)

@bp.route('/projects/<int:id>', methods=['GET'])
@token_auth.login_required
def get_project(id):
    """獲取項目詳情"""
    project = Project.query.get_or_404(id)
    if project.user_id != token_auth.current_user().id:
        return error_response(403, _('Access denied'))
    return jsonify(project.to_dict())

@bp.route('/projects', methods=['POST'])
@token_auth.login_required
def create_project():
    """創建新項目"""
    data = request.get_json() or {}
    if 'title' not in data:
        return bad_request(_('Must include title field'))
    
    project = Project()
    project.from_dict(data, token_auth.current_user())
    db.session.add(project)
    db.session.commit()
    
    response = jsonify(project.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_project', id=project.id)
    return response

@bp.route('/projects/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_project(id):
    """更新項目"""
    project = Project.query.get_or_404(id)
    if project.user_id != token_auth.current_user().id:
        return error_response(403, _('Access denied'))
    
    data = request.get_json() or {}
    project.from_dict(data, token_auth.current_user())
    db.session.commit()
    return jsonify(project.to_dict())

@bp.route('/projects/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_project(id):
    """刪除項目"""
    project = Project.query.get_or_404(id)
    if project.user_id != token_auth.current_user().id:
        return error_response(403, _('Access denied'))
    
    db.session.delete(project)
    db.session.commit()
    return '', 204

@bp.route('/projects/<int:id>/share', methods=['POST'])
@token_auth.login_required
def share_project(id):
    """分享項目"""
    project = Project.query.get_or_404(id)
    if project.user_id != token_auth.current_user().id:
        return error_response(403, _('Access denied'))
    
    project.is_public = True
    db.session.commit()
    
    share_url = url_for('main.project_detail', id=project.id, _external=True)
    return jsonify({
        'status': 'success',
        'share_url': share_url
    }) 