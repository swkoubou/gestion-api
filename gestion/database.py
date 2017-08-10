import os
import configparser

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


BASE_DIR = os.path.abspath('.')

cnf = configparser.ConfigParser()
if cnf.read(os.path.join(BASE_DIR, 'gestion/config/system.cnf')) == []:
    print('設定ファイルが見つかりません。config/system.cnfを作成してください。')

user = password = host = dbname = ''
try:
    user = cnf['mysql']['username']
    password = cnf['mysql']['password']
    host = cnf['mysql']['host']
    dbname = cnf['mysql']['dbname']
except KeyError as err:
    print(f'設定 {err} が見つかりません。追加してください。')

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{dbname}?charset=utf8')
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
Base = declarative_base()
Base.query = session.query_property()


def init_database():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import gestion.models
    Base.metadata.create_all(bind=engine)
