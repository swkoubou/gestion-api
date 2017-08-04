from flask import request as rq
from flask import abort, jsonify
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from gestion.models import Group, User
from gestion.database import session as ss


class GroupList(MethodView):
    def post(self):
        print(rq.form)
        if set(rq.form) != {'name', 'email', 'first_name', 'last_name',
                            'gender', 'password'}: abort(400)
        query = ss.query(Group).filter_by(name=rq.form['name'])
        if query.count() > 0: abort(409, 'そのグループ名は既に使われています')
        group = Group(name=rq.form['name'])
        ss.add(group)
        ss.commit()
        admin = User(email=rq.form['email'], first_name=rq.form['first_name'],
                     last_name=rq.form['last_name'], gender=rq.form['gender'],
                     password=generate_password_hash(rq.form['password']),
                     group_id=group.id)
        ss.add(admin)
        ss.commit()
        return jsonify({
            'group': {'id': group.id, 'name': group.name},
            'user': {'id': admin.id, 'email': admin.email,
                     'first_name': admin.first_name, 'last_name': admin.last_name,
                     'access_token': 'N0IHdzb2MiLCJzdWIiOiJBQkNERUYiLCJhdWQiOiJJSktMTU4iLCJ'}
            })
