from flask import request as rq
from flask import abort, jsonify
from flask.views import MethodView
from werkzeug.security import generate_password_hash
from gestion.models import Group, User, AttendanceRecord
from gestion.database import session as ss
from gestion.utils import Token
from gestion.views.check_authorize import check_authorize, check_authorize_admin
import datetime


class WalkEnterAPI(MethodView):
    """/users/me/enter"""
    def post(self):
        """出勤."""
        user = check_authorize()
        latest_record = (ss.query(AttendanceRecord)
                         .filter_by(owner_id=user.id)
                         .order_by(AttendanceRecord.id.desc()).first())
        if latest_record is not None and latest_record.end is None:
            abort(409, "既に出勤しています")
        record = AttendanceRecord(
            begin=datetime.datetime.now(),
            owner_id=user.id
        )
        ss.add(record)
        ss.commit()
        print('go to walk at %s' % record.begin)
        record = vars(record)
        del record['_sa_instance_state']
        del record['owner_id']
        return jsonify(record)


class WalkExitAPI(MethodView):
    """/users/me/exit"""
    def post(self):
        """退勤."""
        pass


class AttendanceRecordMe(MethodView):
    """/users/me/attendance_records"""
    def get(self):
        """自分の勤務時間一覧の取得."""
        pass


class AttendanceRecordList(MethodView):
    """/users/<int:user_id>/attendance_records"""
    def get(self, user_id):
        """勤務時間一覧の取得."""
        pass
