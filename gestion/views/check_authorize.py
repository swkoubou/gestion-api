from flask import request as rq
from flask import abort, jsonify
from gestion.database import session as ss
from gestion.models import User
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
    user = (ss.query(User)
            .filter_by(id=user_id, group_id=group_id, token=access_token)
            .first()) # 万一重複があった場合の処理が必要？
    if not user:
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
    admin = (ss.query(User)
             .filter_by(id=user_id, group_id=group_id,
                        token=access_token, permission='admin')
             .first())
    if not admin:
        abort(401, '認証に失敗しました')
    else:
        return admin
