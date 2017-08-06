from flask import Flask, jsonify
from gestion.database import session, init_database
from gestion.views.authorize import AuthorizeSigninAPI, AuthorizeSignoutAPI
from gestion.views.groups import GroupAPI, GroupListAPI
from gestion.views.users import UserAPI, UserListAPI, UserMeAPI
from gestion.views.stress import StressAPI, StressMeAPI
from gestion.views.attendance_records import (
    WalkEnterAPI, WalkExitAPI, AttendanceRecordMe, AttendanceRecordList
)


app = Flask(__name__)


@app.cli.command()
def initdb():
    """DB初期化コマンド."""
    init_database()


@app.teardown_appcontext
def shutdown_session(exception=None):
    """リクエスト終了時の処理."""
    session.remove() # DBとの接続を切る


@app.route('/')
def hello():
    return "Hello, Gestion!"

##### エラーレスポンス (JSON化) #####
@app.errorhandler(400)
def bad_request(err):
    return jsonify(code=err.code, message=err.description)


@app.errorhandler(401)
def unauthorize(err):
    return jsonify(code=err.code, message=err.description)


@app.errorhandler(403)
def forbidden(err):
    return jsonify(code=err.code, message=err.description)


@app.errorhandler(404)
def not_found(err):
    return jsonify(code=err.code, message=err.description)


@app.errorhandler(405)
def method_not_allowed(err):
    return jsonify(code=err.code, message=err.description)


@app.errorhandler(409)
def conflict(err):
    return jsonify(code=err.code, message=err.description)


@app.errorhandler(500)
def internal_server_error(err):
    return jsonify(code=err.code, message=err.description)


##### APIルーティング #####
app.add_url_rule('/authorize/signin',
                 view_func=AuthorizeSigninAPI.as_view('signin'),
                 methods=['POST'])
app.add_url_rule('/authorize/signout',
                 view_func=AuthorizeSignoutAPI.as_view('signout'),
                 methods=['POST'])
app.add_url_rule('/groups',
                 view_func=GroupListAPI.as_view('group_list'),
                 methods=['GET', 'POST',])
app.add_url_rule('/groups/<group_name>',
                 view_func=GroupAPI.as_view('groups'),
                 methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/users',
                 view_func=UserListAPI.as_view('users'),
                 methods=['GET', 'POST'])
app.add_url_rule('/users/me',
                 view_func=UserMeAPI.as_view('users_me'),
                 methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/users/<int:user_id>',
                 view_func=UserAPI.as_view('users_list'),
                 methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/users/me/work/enter',
                 view_func=WalkEnterAPI.as_view('work_enter'),
                 methods=['POST'])
app.add_url_rule('/users/me/work/exit',
                 view_func=WalkExitAPI.as_view('work_exit'),
                 methods=['POST'])
app.add_url_rule('/users/me/attendance_records',
                 view_func=AttendanceRecordMe.as_view('attendance_records_me'),
                 methods=['GET'])
app.add_url_rule('/users/me/stress',
                 view_func=StressMeAPI.as_view('stress_me'),
                 methods=['GET',])
app.add_url_rule('/users/<int:user_id>/stress',
                 view_func=StressAPI.as_view('stress'),
                 methods=['GET',])
