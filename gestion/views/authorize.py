from flask import request as rq
from flask import abort, jsonify
from flask.views import MethodView
from werkzeug.security import check_password_hash
from gestion.models import User
from gestion.database import session as ss
from gestion.utils import Token
from gestion.views.check_authorize import check_authorize


class AuthorizeSigninAPI(MethodView):
    """/authorize/signin"""
    def post(self):
        """サインイン."""
        if set(rq.form) != {'group_name', 'email', 'password'}: abort(400)
        user = ss.query(User).filter_by(email=rq.form['email']).first()
        if user is None: abort(404)
        if not check_password_hash(user.password, rq.form['password']):
            abort(401)
        user = vars(user)
        del user['_sa_instance_state']
        del user['password']
        return jsonify(user)


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
