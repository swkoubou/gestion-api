from sqlalchemy import (Column, Integer, String, Boolean,
                        Date, DateTime, ForeignKey)
from sqlalchemy.orm import relation
from gestion.database import Base


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    users = relation('User', backref='users')

    def __repr__(self):
        return f'<Group (id:{self.id} name:{self.name})>'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(254), nullable=False, unique=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    gender = Column(String(10), nullable=False)
    password = Column(String(200), nullable=False)
    token = Column(String(200), nullable=False, unique=True)
    fitbit_id = Column(String(50), nullable=False)
    fitbit_access_token = Column(String(200), nullable=False)
    fitbit_refresh_token = Column(String(200), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'))
    permission_id = Column(Integer, ForeignKey('permissions.id'))

    stress_data = relation('Stress', backref='stress_data')
    attendance_records = relation('AttendanceRecord', backref='attendance_records')

    def __repr__(self):
        return f'<User (id:{self.id} name:{self.email})>'


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)

    def __repr__(self):
        return f'<Permission (id:{self.id} name:{self.name})>'


class Stress(Base):
    __tablename__ = 'stress_data'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    stress = Column(Boolean, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return f'<Stress (id:{self.id} stress?:{self.stress})>'


class AttendanceRecord(Base):
    __tablename__ = 'attendance_records'
    
    id = Column(Integer, primary_key=True)
    begin = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return f'<AttendanceRecord (id:{self.id} begin:{self.begin} end:{self.end})>'
