from flask import Flask, jsonify
from gestion.database import session, init_database
from gestion.views import (
    AuthorizeSigninAPI, AuthorizeSignoutAPI, GroupListAPI, GroupAPI
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
