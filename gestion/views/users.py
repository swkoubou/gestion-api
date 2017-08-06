from flask import request as rq
from flask import abort, jsonify
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from gestion.models import Group, User, Permission, Stress
from gestion.database import session as ss
from gestion.utils import Token
from gestion.views.check_authorize import check_authorize, check_authorize_admin


class UserListAPI(MethodView):
    """/users"""
    def get(self):
        """ユーザ一覧の取得."""
        user = check_authorize()
        users = []
        for u in ss.query(User).filter_by(group_id=user.group_id):
            u = vars(u)
            del u['_sa_instance_state']
            del u['password']
            del u['permission_id']
            del u['token']
            del u['fitbit_id']
            del u['fitbit_access_token']
            del u['fitbit_refresh_token']
            users.append(u)
        return jsonify(users)
    
    def post(self):
        """ユーザの追加."""
        admin = check_authorize_admin()
        if set(rq.form) != {'email', 'first_name', 'last_name',
                            'gender', 'password'}: abort(400)
        query = ss.query(User).filter_by(email=rq.form['email'])
        if query.count() > 0: abort(409, 'そのメールアドレスは既に使われています')
        permission = ss.query(Permission).filter(Permission.name=='user').first()
        new_user = User(email=rq.form['email'], first_name=rq.form['first_name'],
                        last_name=rq.form['last_name'], gender=rq.form['gender'],
                        password=generate_password_hash(rq.form['password']),
                        # user_idが決まらないとアクセストークンが作れないのでダミーを入れる
                        token=Token.generate(0, 0),
                        fitbit_id='', fitbit_access_token='', fitbit_refresh_token='',
                        permission_id=permission.id, group_id=admin.group_id)
        ss.add(new_user)
        ss.commit()
        new_user.token = Token.generate(new_user.id, new_user.group_id)
        ss.commit()
        # commit()後一度オブジェクトを参照しないとvars()で表示できない??
        print('add', new_user.first_name)
        new_user = vars(new_user)
        del new_user['_sa_instance_state']
        del new_user['password']
        del new_user['permission_id']
        del new_user['fitbit_id']
        del new_user['fitbit_access_token']
        del new_user['fitbit_refresh_token']
        del new_user['token']
        return jsonify(new_user)


class UserMeAPI(MethodView):
    """/users/me"""
    def get(self):
        """ユーザ情報の取得(自分)."""
        user = check_authorize()
        user = vars(user)
        del user['_sa_instance_state']
        del user['permission_id']
        del user['password']
        return jsonify(user)

    def put(self):
        """ユーザ情報の更新(自分)."""
        user = check_authorize()
        if 'email' in rq.form:
            query = ss.query(User).filter_by(email=rq.form['email'])
            if query.count() > 0: abort(409, 'そのメールアドレスは既に使われています')
            else: user.email = rq.form['email']
        if 'first_name' in rq.form: user.first_name = rq.form['first_name']
        if 'last_name' in rq.form: user.last_name = rq.form['last_name']
        if 'gender' in rq.form: user.gender = rq.form['gender']
        if 'password' in rq.form: user.password = rq.form['password']
        if 'fitbit_id' in rq.form: user.fitbit_id = rq.form['fitbit_id']
        if 'fitbit_access_token' in rq.form: user.fitbit_access_token = rq.form['fitbit_access_token']
        if 'fitbit_refresh_token' in rq.form: user.fitbit_refresh_token = rq.form['fitbit_refresh_token']
        if ss.dirty: ss.commit()
        # commit()後一度オブジェクトを参照しないとvars()で表示できない??
        print('add', user.first_name)
        user = vars(user)
        del user['_sa_instance_state']
        del user['permission_id']
        del user['password']
        return jsonify(user)


    def delete(self):
        """ユーザの削除(自分)."""
        user = check_authorize()
        ss.delete(user)
        ss.commit()
        return jsonify(message='Good Bye!')


class UserAPI(MethodView):
    """/users/<int:user_id>"""
    def get(self, user_id):
        """ユーザ情報の取得."""
        own = check_authorize()
        user = ss.query(User).filter_by(id=user_id, group_id=own.group_id).first()
        if user is None: abort(404)
        user = vars(user)
        del user['_sa_instance_state']
        del user['permission_id']
        del user['password']
        del user['token']
        del user['fitbit_id']
        del user['fitbit_access_token']
        del user['fitbit_refresh_token']
        return jsonify(user)

    def put(self, user_id):
        """ユーザ情報の更新."""
        pass

    def delete(self, user_id):
        """ユーザの削除."""
        admin = check_authorize_admin()
        user = ss.query(User).filter_by(id=user_id, group_id=admin.group_id).first()
        if user is None: abort(404)
        ss.delete(user)
        ss.commit()
        return jsonify(message='Good Bye!')
