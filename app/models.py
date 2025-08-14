from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # user, premium, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    projects = db.relationship('Project', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_premium(self):
        return self.role in ['premium', 'admin']

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    style = db.Column(db.String(50))
    mood = db.Column(db.String(50))
    tempo = db.Column(db.Integer)
    duration = db.Column(db.Float)
    chord_progression = db.Column(db.String(100))
    midi_path = db.Column(db.String(255))
    audio_path = db.Column(db.String(255))
    is_public = db.Column(db.Boolean, default=False)
    music_files = db.relationship('MusicFile', backref='project', lazy='dynamic')
    
    def __repr__(self):
        return f'<Project {self.title}>'

class MusicFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer, default=30)  # 音乐时长（秒）
    temperature = db.Column(db.Float, default=0.8)  # 生成温度
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MusicFile {self.id}>' 