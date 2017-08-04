from flask import request as rq
from flask import abort, jsonify
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from gestion.models import Group, User, Permission
from gestion.database import session as ss
from gestion.utils import generate_token


class GroupListAPI(MethodView):
    def get(self):
        """グループ一覧取得."""
        groups = [{'id': g.id, 'name': g.name} for g in ss.query(Group)]
        return jsonify(groups)

    def post(self):
        """新規グループと管理ユーザの追加."""
        if set(rq.form) != {'name', 'email', 'first_name', 'last_name',
                            'gender', 'password'}: abort(400)
        query = ss.query(Group).filter_by(name=rq.form['name'])
        if query.count() > 0: abort(409, 'そのグループ名は既に使われています')
        query = ss.query(User).filter_by(email=rq.form['email'])
        if query.count() > 0: abort(409, 'そのメールアドレスは既に使われています')
        # グループの作成
        group = Group(name=rq.form['name'])
        ss.add(group)
        ss.commit()
        # 管理者ユーザの作成
        permission = ss.query(Permission).filter(Permission.name=='admin').first()
        admin = User(email=rq.form['email'], first_name=rq.form['first_name'],
                     last_name=rq.form['last_name'], gender=rq.form['gender'],
                     password=generate_password_hash(rq.form['password']),
                     token=generate_token(),
                     fitbit_id='', fitbit_access_token='', fitbit_refresh_token='',
                     permission_id=permission.id, group_id=group.id)
        ss.add(admin)
        ss.commit()
        return jsonify({
            'group': {'id': group.id, 'name': group.name},
            'user': {
                'id': admin.id, 'email': admin.email,
                'first_name': admin.first_name, 'last_name': admin.last_name,
                'gender': admin.gender, 'access_token': admin.token,
                'group_id': admin.group_id,
                'fitbit': {
                    'fitbit_id': admin.fitbit_id,
                    'access_token': admin.fitbit_access_token,
                    'refresh_token': admin.fitbit_refresh_token,
                }
            }
        })


class GroupAPI(MethodView):
    def get(self, group_name):
        """グループ情報の取得."""
        group = ss.query(Group).filter(Group.name==group_name).first()
        return jsonify(id=group.id, name=group.name)

    def put(self, group_name):
        """グループ情報の変更."""
        ### Need Admin ###
        query = ss.query(Group).filter_by(name=rq.form['name'])
        if query.count() > 0: abort(409, 'そのグループ名は既に使われています')
        group = ss.query(Group).filter(Group.name==group_name).first()
        group.name = rq.form['name']
        ss.commit()
        return jsonify(id=group.id, name=group.name)

    def delete(self, group_name):
        """グループの削除."""
        ### Need Admin ###
        group = ss.query(Group).filter(Group.name==group_name).first()
        ss.delete(group)
        return jsonify(message='Good Bye!')
