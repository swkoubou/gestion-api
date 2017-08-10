from flask import request as rq
from flask import abort, jsonify
from flask.views import MethodView
from werkzeug.security import generate_password_hash
from gestion.models import Group, User
from gestion.database import session as ss
from gestion.utils import Token
from gestion.views.check_authorize import check_authorize, check_authorize_admin


class GroupListAPI(MethodView):
    """/groups"""
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
        admin = User(email=rq.form['email'], first_name=rq.form['first_name'],
                     last_name=rq.form['last_name'], gender=rq.form['gender'],
                     password=generate_password_hash(rq.form['password']),
                     # user_idが決まらないとアクセストークンが作れないのでダミーを入れる
                     token=Token.generate(0, 0),
                     fitbit_id='', fitbit_access_token='', fitbit_refresh_token='',
                     permission='admin', group_id=group.id)
        ss.add(admin)
        ss.commit()
        admin.token = Token.generate(admin.id, admin.group_id)
        ss.commit()
        # commit()後一度オブジェクトを参照しないとvars()で表示できない??
        print('add', admin.first_name)
        admin = vars(admin)
        del admin['_sa_instance_state']
        del admin['password']
        return jsonify({
            'group': {'id': group.id, 'name': group.name},
            'admin': admin,
            })


class GroupAPI(MethodView):
    """/groups/<str:group_name>"""
    def get(self, group_name):
        """グループ情報の取得."""
        group = ss.query(Group).filter(Group.name==group_name).first()
        if group is None: abort(404)
        return jsonify(id=group.id, name=group.name)

    def put(self, group_name):
        """グループ情報の変更."""
        admin = check_authorize_admin()
        group = ss.query(Group).filter_by(name=group_name).first() # URLのグループ
        if not group: abort(404)
        if not admin or admin.group_id != group.id:
            abort(403) 
        if 'name' not in rq.form: abort(400)
        query = ss.query(Group).filter_by(name=rq.form['name'])
        if query.count() > 0: abort(409, 'そのグループ名は既に使われています')
        group.name = rq.form['name']
        ss.commit()
        return jsonify(id=group.id, name=group.name)

    def delete(self, group_name):
        """グループの削除."""
        admin = check_authorize_admin()
        group = ss.query(Group).filter_by(name=group_name).first() # URLのグループ
        if not group: abort(404)
        if not admin or admin.group_id != group.id:
            abort(403) 
        ss.delete(group)
        ss.commit()
        return jsonify(message='Good Bye!')
