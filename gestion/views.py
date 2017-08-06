from flask import request as rq
from flask import abort, jsonify
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from gestion.models import Group, User, Permission
from gestion.database import session as ss
from gestion.utils import Token


def parse_authorize_header():
    # ヘッダ形式はRFC6750参照
    authorization = rq.headers['Authorization']
    scheme, access_token = authorization.split()
    if scheme != 'Bearer': raise Exception # Bearerスキームの確認
    t = Token(access_token)
    return t.group_id, t.user_id, access_token


def check_authorize():
    """アクセストークンを調べて正しいユーザか確認する."""
    try:
        group_id, user_id, access_token = parse_authorize_header()
    except:
        abort(400, '正しいAuthorizationヘッダが必要です')

    # トークンの照合
    user = ss.query(User).filter_by(id=user_id, group_id=group_id).first()
    if user.token != access_token:
        abort(401, '認証に失敗しました')
    else:
        return user


def check_authorize_admin():
    """アクセストークンを調べて正しい管理ユーザか確認する."""
    try:
        group_id, user_id ,access_token = parse_authorize_header()
    except:
        abort(400, '正しいAuthorizationヘッダが必要です')

    # トークンの照合
    admin = ss.query(User).filter_by(id=user_id, group_id=group_id).first()
    permission = ss.query(Permission).filter(Permission.name=='admin').first()
    if admin.token != access_token or admin.permission_id != permission.id:
        abort(401, '認証に失敗しました')
    else:
        return admin


class AuthorizeSigninAPI(MethodView):
    """/authorize/signin"""
    def post(self):
        """サインイン."""
        if set(rq.form) != {'group_name', 'email', 'password'}: abort(400)
        user = ss.query(User).filter_by(email=rq.form['email']).first()
        if user is None: abort(404)
        if not check_password_hash(user.password, rq.form['password']):
            abort(401)
        return jsonify({
            'id': user.id, 'email': user.email,
            'first_name': user.first_name, 'last_name': user.last_name,
            'gender': user.gender, 'access_token': user.token,
            'group_id': user.group_id, 'fitbit': {
                'fitbit_id': user.fitbit_id,
                'access_token': user.fitbit_access_token,
                'refresh_token': user.fitbit_refresh_token,
            }
        })


class AuthorizeSignoutAPI(MethodView):
    """/authorize/signout"""
    def post(self):
        """サインアウト."""
        user = check_authorize()
        token = Token(user.token)
        token.update()
        user.token = token.tokenize()
        ss.commit()
        return jsonify(message='See you again!')


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
        permission = ss.query(Permission).filter(Permission.name=='admin').first()
        admin = User(email=rq.form['email'], first_name=rq.form['first_name'],
                     last_name=rq.form['last_name'], gender=rq.form['gender'],
                     password=generate_password_hash(rq.form['password']),
                     # user_idが決まらないとアクセストークンが作れないのでダミーを入れる
                     token=Token.generate(0, 0),
                     fitbit_id='', fitbit_access_token='', fitbit_refresh_token='',
                     permission_id=permission.id, group_id=group.id)
        ss.add(admin)
        ss.commit()
        admin.token = Token.generate(admin.id, admin.group_id)
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
    """/groups/<str:group_name>"""
    def get(self, group_name):
        """グループ情報の取得."""
        group = ss.query(Group).filter(Group.name==group_name).first()
        if group is None: abort(404)
        return jsonify(id=group.id, name=group.name)

    def put(self, group_name):
        """グループ情報の変更."""
        user = check_authorize()
        group = ss.query(Group).filter_by(name=group_name).first() # URLのグループ
        admin = ss.query(Permission).filter_by(name='admin').first() # 管理者か
        if user.group_id != group.id or user.permission_id != admin.id:
            abort(403) 
        if group is None: abort(404)
        if 'name' not in rq.form: abort(400)
        query = ss.query(Group).filter_by(name=rq.form['name'])
        if query.count() > 0: abort(409, 'そのグループ名は既に使われています')
        group.name = rq.form['name']
        ss.commit()
        return jsonify(id=group.id, name=group.name)

    def delete(self, group_name):
        """グループの削除."""
        user = check_authorize()
        group = ss.query(Group).filter_by(name=group_name).first() # URLのグループ
        admin = ss.query(Permission).filter_by(name='admin').first() # 管理者か
        if user.group_id != group.id or user.permission_id != admin.id:
            abort(403) 
        if group is None: abort(404)
        group = ss.query(Group).filter(Group.name==group_name).first()
        if group is None: abort(404)
        ss.delete(group)
        ss.commit()
        return jsonify(message='Good Bye!')


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
        del new_user['token']
        return jsonify(new_user)


class UserMeAPI(MethodView):
    """/users/me"""
    def get(self):
        """ユーザ情報の取得(自分)."""
        pass

    def put(self):
        """ユーザ情報の更新(自分)."""
        pass

    def delete(self):
        """ユーザの削除(自分)."""
        pass


class UserAPI(MethodView):
    """/users/<int:user_id>"""
    def get(self, user_id):
        """ユーザ情報の取得."""
        pass

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
