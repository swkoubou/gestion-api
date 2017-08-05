from flask import request as rq
from flask import abort, jsonify
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from gestion.models import Group, User, Permission
from gestion.database import session as ss
from gestion.utils import Token


def check_authorize():
    """アクセストークンを調べて正しいユーザか確認する."""
    try:
        # ヘッダ形式はRFC6750参照
        authorization = rq.headers['Authorization']
        scheme, access_token = authorization.split()
        if scheme != 'Bearer': raise Exception # Bearerスキームの確認
        t = Token(access_token)
    except:
        abort(400, '正しいAuthorizationヘッダが必要です')

    # トークンの照合
    user = ss.query(User).filter_by(id=t.user_id, group_id=t.group_id).first()
    if user.token != access_token:
        abort(401, '認証に失敗しました')
    else:
        return user


class AuthorizeSigninAPI(MethodView):
    """サインイン."""
    def post(self):
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
    """サインアウト."""
    def post(self):
        user = check_authorize()
        token = Token(user.token)
        token.update()
        user.token = token.tokenize()
        ss.commit()
        return jsonify(message='See you again!')


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
