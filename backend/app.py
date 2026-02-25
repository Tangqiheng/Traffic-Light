from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from database import db
from auth import User, create_access_token, create_refresh_token, verify_token
import os

def create_app():
    app = Flask(__name__)
    
    # 配置数据库 - 使用新的数据库文件名
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'sqlite:///./traffic_users.db'  # 与init_db.py一致
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)  # 允许跨域请求
    
    # 创建数据库表
    with app.app_context():
        # 确保导入User模型到Base.metadata中
        from auth import User
        # 创建所有表
        db.create_all()
        print("数据库表创建完成")
        # 创建默认管理员用户
        create_default_admin()
    
    # 注册路由
    register_routes(app)
    
    return app

def create_default_admin():
    """创建默认管理员用户"""
    # 使用db.session.query而不是User.query
    admin_user = db.session.query(User).filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            full_name='系统管理员',
            is_admin=True,
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("默认管理员账户已创建: admin / admin123")

def register_routes(app):
    # 添加根路径处理
    @app.route('/')
    def index():
        return jsonify({
            'message': '智能交通灯控制系统后端服务',
            'status': 'running',
            'version': '1.0.0'
        })
    
    from controllers.traffic_controller import traffic_bp
    app.register_blueprint(traffic_bp, url_prefix='/api/traffic')
    
    # 注册认证路由
    register_auth_routes(app)

def register_auth_routes(app):
    """注册认证相关的路由"""
    # 直接在app.py中定义认证路由，避免导入问题
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """用户登录"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求数据格式错误', 'code': 'INVALID_REQUEST_DATA'}), 400
            
            username = data.get('username')
            password = data.get('password')
            
            # 输入验证
            if not username:
                return jsonify({'error': '用户名不能为空', 'code': 'USERNAME_REQUIRED'}), 400
            
            if not password:
                return jsonify({'error': '密码不能为空', 'code': 'PASSWORD_REQUIRED'}), 400
            
            # 查找用户 - 使用db.session.query
            user = db.session.query(User).filter_by(username=username).first()
            
            # 用户不存在
            if not user:
                return jsonify({
                    'error': '用户名不存在', 
                    'code': 'USER_NOT_FOUND',
                    'details': '请检查用户名是否正确'
                }), 401
            
            # 验证密码
            if not user.verify_password(password):
                return jsonify({
                    'error': '密码错误', 
                    'code': 'INVALID_PASSWORD',
                    'details': '请检查密码是否正确'
                }), 401
            
            # 检查账户状态
            if not (getattr(user, 'is_active', False) is True):
                return jsonify({
                    'error': '账户已被禁用', 
                    'code': 'ACCOUNT_DISABLED',
                    'details': '请联系管理员启用账户'
                }), 401
            
            # 检查是否为管理员账户但密码是默认密码
            if getattr(user, 'username', None) == 'admin' and password == 'admin123':
                access_token = create_access_token({"sub": user.username})
                refresh_token = create_refresh_token({"sub": user.username})
                return jsonify({
                    'error': '安全警告',
                    'code': 'DEFAULT_PASSWORD_WARNING',
                    'details': '检测到您正在使用默认密码，请尽快修改密码以确保账户安全',
                    'access_granted': True,
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'bearer',
                    'message': '登录成功（默认密码警告）'
                }), 200
            
            # 创建令牌
            access_token = create_access_token({"sub": user.username})  # 修复：传递字典而不是字符串
            refresh_token = create_refresh_token({"sub": user.username})  # 修复：传递字典而不是字符串
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'user': user.to_dict(),
                'message': '登录成功'
            })

        except Exception as e:
            import traceback
            print("=== 登录接口异常 ===")
            print(traceback.format_exc())
            print(f"Exception: {e}")
            error_details = {
                'error': f'服务器内部错误: {str(e)}',
                'code': 'INTERNAL_SERVER_ERROR',
                'details': '请稍后重试或联系系统管理员',
                'traceback': traceback.format_exc() if hasattr(traceback, 'format_exc') else str(e)
            }
            return jsonify(error_details), 500
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """用户注册"""
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            full_name = data.get('full_name', '')
            
            if not username or not email or not password:
                return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
            
            # 检查用户名是否已存在 - 使用db.session.query
            if db.session.query(User).filter_by(username=username).first():
                return jsonify({'error': '用户名已存在'}), 400
            
            # 检查邮箱是否已存在 - 使用db.session.query
            if db.session.query(User).filter_by(email=email).first():
                return jsonify({'error': '邮箱已被注册'}), 400
            
            # 创建新用户
            user = User(
                username=username,
                email=email,
                full_name=full_name
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # 创建令牌
            access_token = create_access_token({"sub": user.username})  # 修复：传递字典而不是字符串
            refresh_token = create_refresh_token({"sub": user.username})  # 修复：传递字典而不是字符串

            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'user': user.to_dict()
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    def refresh():
        """刷新访问令牌"""
        try:
            data = request.get_json()
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({'error': '刷新令牌不能为空'}), 400
            
            # 验证刷新令牌
            username = verify_token(refresh_token)
            if not username:
                return jsonify({'error': '无效的刷新令牌'}), 401
            
            # 检查用户是否存在且活跃 - 使用db.session.query
            user = db.session.query(User).filter_by(username=username).first()
            if not user or not (getattr(user, 'is_active', False) is True):
                return jsonify({'error': '用户不存在或已被禁用'}), 401
            
            # 创建新的访问令牌
            new_access_token = create_access_token({"sub": username})  # 修复：传递字典
            
            return jsonify({
                'access_token': new_access_token,
                'token_type': 'bearer'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/me', methods=['GET'])
    def get_current_user():
        """获取当前用户信息"""
        try:
            # 从Authorization头获取令牌
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': '未提供有效的认证令牌'}), 401
            
            token = auth_header.split(' ')[1]
            username = verify_token(token)
            
            if not username:
                return jsonify({'error': '无效的认证令牌'}), 401
            
            # 使用db.session.query查找用户
            user = db.session.query(User).filter_by(username=username).first()
            if not user or not (getattr(user, 'is_active', False) is True):
                return jsonify({'error': '用户不存在或已被禁用'}), 401
            
            return jsonify(user.to_dict())
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def get_traffic_status(intersection_id):
    """获取交通状态"""
    try:
        from services.traffic_service import TrafficService
        service = TrafficService()
        status = service.get_intersection_status(intersection_id)
        return jsonify(status.dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500



def main():
    app = create_app()
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False  # 生产环境应设为False
    )


if __name__ == '__main__':
    main()