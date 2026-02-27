from sqlalchemy import text
from flask import request, jsonify
from database import db
from auth import User
from auth_util import admin_auth_check

def register_admin_user_api(app):
    @app.route('/api/admin/users/<int:user_id>', methods=['GET'])
    def admin_get_user(user_id):
        try:
            _, err, code = admin_auth_check()
            if err:
                return err, code
            user = db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            return jsonify({'user': user.to_dict()})
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    @app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
    def admin_update_user(user_id):
        try:
            _, err, code = admin_auth_check()
            if err:
                return err, code
            user = db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            data = request.get_json()
            # 支持修改id（仅非admin用户，且新id唯一且为正整数）
            new_id = data.get('id')
            if new_id is not None and new_id != user.id:
                try:
                    new_id = int(new_id)
                    if new_id <= 0:
                        return jsonify({'error': 'ID必须为正整数'}), 400
                except Exception:
                    return jsonify({'error': 'ID必须为正整数'}), 400
                # 判断当前user对象的实际username属性
                if getattr(user, 'username', None) == 'admin':
                    return jsonify({'error': '管理员ID不可更改'}), 400
                if db.session.query(User).filter_by(id=new_id).first():
                    return jsonify({'error': '目标ID已存在'}), 400
                # SQLAlchemy主键更新方式（原生SQL）
                db.session.execute(text("UPDATE users SET id = :new_id WHERE id = :old_id"), {"new_id": new_id, "old_id": user.id})
                db.session.commit()
                # 重新获取user对象
                user = db.session.query(User).filter_by(id=new_id).first()
                if user is None:
                    return jsonify({'error': '主键更新后用户丢失'}), 500
            username = (data.get('username') or '').strip()
            email = (data.get('email') or '').strip()
            full_name = (data.get('full_name') or '').strip()
            is_admin = bool(data.get('is_admin', False))
            is_active = bool(data.get('is_active', True))
            # 用户名、邮箱唯一性校验
            if user is not None:
                if username and username != getattr(user, 'username', None):
                    if db.session.query(User).filter_by(username=username).first():
                        return jsonify({'error': '用户名已存在'}), 400
                    user.username = username
                if email and email != getattr(user, 'email', None):
                    if db.session.query(User).filter_by(email=email).first():
                        return jsonify({'error': '邮箱已存在'}), 400
                    user.email = email
                if full_name:
                    user.full_name = full_name
                user.is_admin = is_admin
                user.is_active = is_active
                db.session.commit()
                return jsonify({'success': True, 'user': user.to_dict()})
            else:
                return jsonify({'error': '用户不存在'}), 404
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    @app.route('/api/admin/users/<int:user_id>/reset_password', methods=['POST'])
    def admin_reset_password(user_id):
        try:
            _, err, code = admin_auth_check()
            if err:
                return err, code
            user = db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            data = request.get_json()
            new_password = data.get('new_password', '')
            if not new_password or len(new_password) < 6:
                return jsonify({'error': '新密码长度不能少于6位'}), 400
            user.set_password(new_password)
            db.session.commit()
            return jsonify({'success': True, 'message': '密码重置成功'})
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

    @app.route('/api/admin/users/<int:user_id>/toggle_active', methods=['PATCH'])
    def admin_toggle_active(user_id):
        try:
            _, err, code = admin_auth_check()
            if err:
                return err, code
            user = db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            user.is_active = not bool(user.is_active)
            db.session.commit()
            return jsonify({'success': True, 'is_active': user.is_active})
        except Exception as e:
            import traceback
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
