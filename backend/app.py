from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from database import db
from auth import User, create_access_token, create_refresh_token, verify_token
from auth_util import admin_auth_check
import os
from apscheduler.schedulers.background import BackgroundScheduler
from models import TrafficStat

def create_app():
    # 启动定时采集任务（APScheduler）
    import random
    def collect_traffic_data():
        # 采集模拟数据，实际可替换为真实采集逻辑
        flow = random.randint(30, 60)
        speed = round(random.uniform(30, 45), 2)
        with app.app_context():
            stat = TrafficStat(
                flow=flow,
                speed=speed
            )
            db.session.add(stat)
            db.session.commit()
    scheduler = BackgroundScheduler()
    scheduler.add_job(collect_traffic_data, 'interval', seconds=60)
    scheduler.start()
    app = Flask(__name__)
    # 配置数据库 - 使用新的数据库文件名
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@localhost:3306/traffic_db?charset=utf8mb4"
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
    # 注册admin用户管理接口
    try:
        from admin_user_api_patch import register_admin_user_api
        register_admin_user_api(app)
    except Exception as e:
        print(f"[警告] 注册admin用户管理接口失败: {e}")
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
    """注册所有路由"""
    # 统计数据接口，兼容前端 /api/traffic/statistics
    @app.route('/api/traffic/statistics')
    def traffic_statistics():
        from flask import jsonify, request
        from models import TrafficStat
        hours = int(request.args.get('hours', 24))
        # 查询最近hours小时的统计数据
        import datetime
        now = datetime.datetime.now()
        since = now - datetime.timedelta(hours=hours)
        stats = TrafficStat.query.filter(TrafficStat.timestamp >= since).order_by(TrafficStat.timestamp.asc()).all()
        points = []
        for stat in stats:
            points.append({
                'time': stat.timestamp.strftime('%H:%M'),
                'total_vehicles': stat.flow,
                'average_speed': stat.speed
            })
        # 按小时聚合（可选）
        hourly_distribution = []
        if points:
            from collections import defaultdict
            hour_map = defaultdict(list)
            for stat in stats:
                hour = stat.timestamp.hour
                hour_map[hour].append(stat)
            for hour, stats_in_hour in hour_map.items():
                avg_flow = int(sum(s.flow for s in stats_in_hour) / len(stats_in_hour))
                avg_speed = round(sum(s.speed for s in stats_in_hour) / len(stats_in_hour), 2)
                hourly_distribution.append({
                    'hour': hour,
                    'average_vehicles': avg_flow,
                    'average_speed': avg_speed
                })
            hourly_distribution.sort(key=lambda x: x['hour'])
        return jsonify({
            'data': {
                'points': points,
                'hourly_distribution': hourly_distribution
            }
        })
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
    # 注册动态交通数据接口，兼容前端/api/traffic/data
    from services.traffic_service import TrafficService
    @app.route('/api/traffic/data')
    def traffic_data():
        from flask import jsonify, request
        import time
        intersection_id = request.args.get('intersection_id', 'intersection_001')
        status = TrafficService.get_traffic_status(intersection_id)
        lanes = status.lanes
        total_vehicles = sum(lane.vehicle_count for lane in lanes)
        avg_speed = round(sum(lane.average_speed for lane in lanes) / len(lanes), 1) if lanes else 0
        # 信号灯模拟
        now = int(time.time())
        cycle = now % 70
        # 南北方向
        if cycle < 30:
            ns_status, ns_countdown = "绿灯", 30 - cycle
        elif cycle < 35:
            ns_status, ns_countdown = "黄灯", 35 - cycle
        else:
            ns_status, ns_countdown = "红灯", 70 - cycle
        # 东西方向
        if cycle < 35:
            ew_status, ew_countdown = "红灯", 35 - cycle
        elif cycle < 65:
            ew_status, ew_countdown = "绿灯", 65 - cycle
        else:
            ew_status, ew_countdown = "黄灯", 70 - cycle
        # 保证倒计时为0时立即切换状态，不会出现0后又回跳
        if ns_countdown == 0:
            if ns_status == "绿灯":
                ns_status, ns_countdown = "黄灯", 5
            elif ns_status == "黄灯":
                ns_status, ns_countdown = "红灯", 35
            elif ns_status == "红灯":
                ns_status, ns_countdown = "绿灯", 30
        if ew_countdown == 0:
            if ew_status == "绿灯":
                ew_status, ew_countdown = "黄灯", 5
            elif ew_status == "黄灯":
                ew_status, ew_countdown = "红灯", 35
            elif ew_status == "红灯":
                ew_status, ew_countdown = "绿灯", 30
        lights = {
            "north": {"status": ns_status, "countdown": ns_countdown},
            "south": {"status": ns_status, "countdown": ns_countdown},
            "east": {"status": ew_status, "countdown": ew_countdown},
            "west": {"status": ew_status, "countdown": ew_countdown}
        }
        return jsonify({
            "data": [{
                "intersection_id": intersection_id,
                "timestamp": status.timestamp.isoformat(),
                "vehicle_count": total_vehicles,
                "average_speed": avg_speed,
                "congestion_level": "正常",
                "lights": lights
            }]
        })
    # 注册认证路由
    register_auth_routes(app)

def register_auth_routes(app):
    from models import OperationLog, UserPermission

    def log_operation(user, action, detail=None):
        log = OperationLog()
        log.user_id = getattr(user, 'id', None)
        log.username = getattr(user, 'username', None)
        log.action = action
        log.detail = detail
        db.session.add(log)
        db.session.commit()

    @app.route('/api/admin/logs', methods=['GET'])
    def get_operation_logs():
        """查询操作日志，支持分页和条件"""
        _, err, code = admin_auth_check()
        if err:
            return err, code
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        username = request.args.get('username')
        query = db.session.query(OperationLog)
        if username:
            query = query.filter(OperationLog.username == username)
        total = query.count()
        logs = query.order_by(OperationLog.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
        return jsonify({
            'logs': [dict(id=l.id, user_id=l.user_id, username=l.username, action=l.action, detail=l.detail, created_at=l.created_at.isoformat()) for l in logs],
            'total': total, 'page': page, 'page_size': page_size
        })

    @app.route('/api/admin/permissions/<int:user_id>', methods=['GET'])
    def get_user_permissions(user_id):
        """查询用户权限"""
        _, err, code = admin_auth_check()
        if err:
            return err, code
        perms = db.session.query(UserPermission).filter_by(user_id=user_id).all()
        return jsonify({'permissions': [p.permission for p in perms]})

    @app.route('/api/admin/permissions/<int:user_id>', methods=['POST'])
    def set_user_permissions(user_id):
        """设置用户权限（覆盖式）"""
        admin, err, code = admin_auth_check()
        if err:
            return err, code
        data = request.get_json()
        permissions = data.get('permissions', [])
        if not isinstance(permissions, list):
            return jsonify({'error': 'permissions必须为列表'}), 400
        # 先删除原有
        db.session.query(UserPermission).filter_by(user_id=user_id).delete()
        # 新增
        for perm in permissions:
            up = UserPermission()
            up.user_id = user_id
            up.permission = perm
            db.session.add(up)
        db.session.commit()
        log_operation(admin, f'分配权限', f'user_id={user_id}, permissions={permissions}')
        return jsonify({'success': True})
    @app.route('/api/user/profile', methods=['GET'])
    def get_user_profile():
        """获取当前用户信息（兼容前端 profile 获取）"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': '未提供有效的认证令牌'}), 401
            token = auth_header.split(' ')[1]
            username = verify_token(token)
            if not username:
                return jsonify({'error': '无效的认证令牌'}), 401
            user = db.session.query(User).filter_by(username=username).first()
            if not user or not (getattr(user, 'is_active', False) is True):
                return jsonify({'error': '用户不存在或已被禁用'}), 401
            return jsonify(user.to_dict())
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    @app.route('/api/auth/change_password', methods=['POST'])
    def change_password():
        """修改当前用户密码"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': '未提供有效的认证令牌'}), 401
            token = auth_header.split(' ')[1]
            username = verify_token(token)
            if not username:
                return jsonify({'error': '无效的认证令牌'}), 401
            user = db.session.query(User).filter_by(username=username).first()
            if not user or not (getattr(user, 'is_active', False) is True):
                return jsonify({'error': '用户不存在或已被禁用'}), 401

            data = request.get_json()
            if not data:
                return jsonify({'error': '请求数据格式错误'}), 400
            old_password = data.get('old_password', '')
            new_password = data.get('new_password', '')

            if not old_password or not new_password:
                return jsonify({'error': '请填写完整的旧密码和新密码'}), 400
            if len(new_password) < 6:
                return jsonify({'error': '新密码长度不能少于6位'}), 400
            if len(new_password.encode('utf-8')) > 72:
                return jsonify({'error': '新密码不能超过72字节'}), 400
            if not user.verify_password(old_password):
                return jsonify({'error': '旧密码错误'}), 400
            if old_password == new_password:
                return jsonify({'error': '新密码不能与旧密码相同'}), 400

            user.set_password(new_password)
            db.session.commit()
            return jsonify({'success': True, 'message': '密码修改成功'})
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    @app.route('/api/user/profile', methods=['PUT'])
    def update_profile():
        """修改当前用户信息（用户名、邮箱、姓名）"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': '未提供有效的认证令牌'}), 401
            token = auth_header.split(' ')[1]
            username = verify_token(token)
            if not username:
                return jsonify({'error': '无效的认证令牌'}), 401
            user = db.session.query(User).filter_by(username=username).first()
            if not user or not (getattr(user, 'is_active', False) is True):
                return jsonify({'error': '用户不存在或已被禁用'}), 401
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求数据格式错误'}), 400
            new_username = (data.get('username') or '').strip()
            new_email = (data.get('email') or '').strip()
            new_full_name = (data.get('full_name') or '').strip()
            # 用户名校验
            if not new_username:
                return jsonify({'error': '用户名不能为空'}), 400
            if new_username != user.username:
                exists = db.session.query(User).filter_by(username=new_username).first()
                if exists:
                    return jsonify({'error': '该用户名已被占用'}), 400
            if new_email and new_email != user.email:
                if db.session.query(User).filter_by(email=new_email).first():
                    return jsonify({'error': '该邮箱已被占用'}), 400
                user.email = new_email
            if new_full_name:
                user.full_name = new_full_name
            username_changed = False
            if new_username != user.username:
                user.username = new_username
                username_changed = True
            db.session.commit()
            result = user.to_dict()
            result['username_changed'] = str(username_changed)
            return jsonify(result)
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    # 管理员用户管理接口（分页、查询、批量、增删改查）
    from sqlalchemy import or_


    @app.route('/api/admin/users', methods=['GET'])
    def admin_list_users():
        """分页+条件查询用户"""
        try:
            _, err, code = admin_auth_check()
            if err:
                return err, code
            # 分页参数
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 10))
            # 查询条件
            q = (request.args.get('q') or '').strip()
            is_active = request.args.get('is_active')
            is_admin = request.args.get('is_admin')
            query = db.session.query(User)
            if q:
                username_col = User.__dict__['username']
                email_col = User.__dict__['email']
                full_name_col = User.__dict__['full_name']
                query = query.filter(or_(username_col.like(f'%{q}%'), email_col.like(f'%{q}%'), full_name_col.like(f'%{q}%')))
            if is_active is not None:
                is_active_col = User.__dict__['is_active']
                if is_active.lower() == 'true':
                    query = query.filter(is_active_col == True)
                elif is_active.lower() == 'false':
                    query = query.filter(is_active_col == False)
            if is_admin is not None:
                is_admin_col = User.__dict__['is_admin']
                if is_admin.lower() == 'true':
                    query = query.filter(is_admin_col == True)
                elif is_admin.lower() == 'false':
                    query = query.filter(is_admin_col == False)
            total = query.count()
            # 自定义排序：管理员（admin）优先，其余按sort_order升序、id升序
            from sqlalchemy import desc, case
            username_col = getattr(User, 'username')
            sort_order_col = getattr(User, 'sort_order')
            id_col = getattr(User, 'id')
            users = query.order_by(
                desc(case((username_col == 'admin', 1), else_=0)),  # admin优先
                sort_order_col.asc(),                               # 其余按sort_order升序
                id_col.asc()                                        # 再按id升序
            ).offset((page-1)*page_size).limit(page_size).all()
            return jsonify({'users': [u.to_dict() for u in users], 'total': total, 'page': page, 'page_size': page_size})
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    @app.route('/api/admin/users', methods=['POST'])
    def admin_add_user():
        """添加用户"""
        try:
            _, err, code = admin_auth_check()
            if err:
                return err, code
            data = request.get_json()
            username = (data.get('username') or '').strip()
            email = (data.get('email') or '').strip()
            full_name = (data.get('full_name') or '').strip()
            password = data.get('password') or ''
            is_admin = bool(data.get('is_admin', False))
            is_active = bool(data.get('is_active', True))
            # 校验
            if not username or not email or not password:
                return jsonify({'error': '请填写完整的用户名、邮箱和密码'}), 400
            if db.session.query(User).filter_by(username=username).first():
                return jsonify({'error': '用户名已存在'}), 400
            if db.session.query(User).filter_by(email=email).first():
                return jsonify({'error': '邮箱已存在'}), 400
            user = User(username=username, email=email, full_name=full_name, is_admin=is_admin, is_active=is_active)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return jsonify({'success': True, 'user': user.to_dict()})
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    @app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
    def admin_delete_user(user_id):
        """删除单个用户"""
        try:
            _, err, code = admin_auth_check()
            if err:
                return err, code
            user = db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            db.session.delete(user)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    @app.route('/api/admin/users/batch_delete', methods=['POST'])
    def admin_batch_delete_users():
        """批量删除用户"""
        try:
            _, err, code = admin_auth_check()
            if err:
                return err, code
            data = request.get_json()
            ids = data.get('ids', [])
            if not ids or not isinstance(ids, list):
                return jsonify({'error': '请提供要删除的用户ID列表'}), 400
            users = db.session.query(User).filter(User.id.in_(ids)).all()
            for user in users:
                db.session.delete(user)
            db.session.commit()
            return jsonify({'success': True, 'deleted': len(users)})
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    @app.route('/api/auth/login', methods=['POST'])


    def login():
        """用户登录"""
        import os
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'login_debug.log')
        def log_msg(msg):
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(msg + '\n')
        try:
            data = request.get_json()
            if not data:
                log_msg('[ERROR] 请求数据格式错误')
                return jsonify({'error': '请求数据格式错误', 'code': 'INVALID_REQUEST_DATA'}), 400
            username = data.get('username')
            password = data.get('password')
            log_msg(f"[DEBUG] Received password: {repr(password)}, length: {len(password)}")

            # 输入验证
            if not username:
                log_msg('[ERROR] 用户名不能为空')
                return jsonify({'error': '用户名不能为空', 'code': 'USERNAME_REQUIRED'}), 400
            if not password:
                log_msg('[ERROR] 密码不能为空')
                return jsonify({'error': '密码不能为空', 'code': 'PASSWORD_REQUIRED'}), 400

            # 查找用户 - 使用db.session.query
            user = db.session.query(User).filter_by(username=username).first()
            # 用户不存在
            if not user:
                log_msg('[ERROR] 用户不存在')
                return jsonify({
                    'error': '用户名不存在',
                    'code': 'USER_NOT_FOUND',
                    'details': '请检查用户名是否正确'
                }), 401

            # 密码长度校验（bcrypt最大支持72字节）
            try:
                if len(password.encode('utf-8')) > 72:
                    log_msg(f"[ERROR] Password too long: {len(password.encode('utf-8'))} bytes")
                    return jsonify({
                        "code": "PASSWORD_TOO_LONG",
                        "error": "password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72])"
                    }), 400
            except Exception as e:
                log_msg(f"[ERROR] 密码编码异常: {str(e)}")
                return jsonify({
                    'error': f'密码编码异常: {str(e)}',
                    'code': 'PASSWORD_ENCODING_ERROR',
                    'details': '请检查密码内容是否为有效字符'
                }), 400

            # 只有长度校验通过后才进行密码校验
            if not user.verify_password(password):
                log_msg('[ERROR] 密码错误')
                return jsonify({
                    'error': '密码错误',
                    'code': 'INVALID_PASSWORD',
                    'details': '请检查密码是否正确'
                }), 401

            # 检查账户状态
            if not (getattr(user, 'is_active', False) is True):
                log_msg('[ERROR] 账户已被禁用')
                return jsonify({
                    'error': '账户已被禁用',
                    'code': 'ACCOUNT_DISABLED',
                    'details': '请联系管理员启用账户'
                }), 401

            # 检查是否为管理员账户但密码是默认密码
            if getattr(user, 'username', None) == 'admin' and password == 'admin123':
                log_msg('[WARN] 管理员使用默认密码登录')
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
            log_msg('[INFO] 登录成功')
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'user': user.to_dict(),
                'message': '登录成功'
            })
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            log_msg(f"[EXCEPTION] {e}\n{tb}")
            error_details = {
                'error': f'服务器内部错误: {str(e)}',
                'code': 'INTERNAL_SERVER_ERROR',
                'details': '请稍后重试或联系系统管理员',
                'traceback': tb
            }
            return jsonify(error_details), 500
    
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
            if not user:
                return jsonify({"code": "USER_NOT_FOUND", "error": "用户名不存在"}), 401

            # 创建新的访问令牌
            new_access_token = create_access_token({"sub": username})  # 修复：传递字典

            return jsonify({
                'access_token': new_access_token,
                'token_type': 'bearer'
            })
        except Exception as e:
            import traceback
            print(f"[EXCEPTION] {e}\n{traceback.format_exc()}")
            return jsonify({
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(e),
                "error": "服务器内部错误，请联系管理员。",
                "traceback": traceback.format_exc()
            }), 500
    
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
    # 启动时测试日志写入
    import os
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'startup.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write('后端启动日志写入测试\n')
    except Exception as e:
        raise RuntimeError(f"无法写入日志文件: {log_path}, 错误: {e}")
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False  # 生产环境应设为False
    )


if __name__ == '__main__':
    main()

# 仅在被导入时创建 app 实例，避免 NameError
if __name__ != "__main__":
    app = create_app()