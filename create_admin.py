from app import create_app, db
from app.models import User

def create_admin():
    app = create_app()
    with app.app_context():
        # 检查是否已存在管理员账号
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('管理员账号创建成功！')
            print('用户名: admin')
            print('密码: admin123')
        else:
            print('管理员账号已存在！')

if __name__ == '__main__':
    create_admin() 