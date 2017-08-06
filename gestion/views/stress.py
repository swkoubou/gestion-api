from flask import request as rq
from flask import abort, jsonify
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from gestion.models import Group, User, Permission, Stress
from gestion.database import session as ss
from gestion.utils import Token
from gestion.views.check_authorize import check_authorize, check_authorize_admin


class StressMeAPI(MethodView):
    """/users/me/stress"""
    def get(self):
        """自分のストレス値一覧の取得."""
        user = check_authorize()
        stress_data = [{'value': s.stress, 'date': s.date.isoformat()}
                       for s in ss.query(Stress).filter_by(owner_id=user.id)]
        return jsonify(stress_data)


class StressAPI(MethodView):
    """/users/<int:user_id>/stress"""
    def get(self, user_id):
        """ストレス値一覧の取得."""
        admin = check_authorize_admin()
        user = ss.query(User).filter_by(id=user_id, group_id=admin.group_id).first()
        if user is None: abort(404)
        stress_data = [{'value': s.stress, 'date': s.date.isoformat()}
                       for s in ss.query(Stress).filter_by(owner_id=user.id)]
        return jsonify(stress_data)
