from gestion.database import session
from gestion.models import User, Stress
import configparser, os
import requests

BASE_DIR = os.path.abspath('.')

cnf = configparser.ConfigParser()
if cnf.read(os.path.join(BASE_DIR, 'gestion/config/system.cnf')) == []:
    print('設定ファイルが見つかりません。config/system.cnfを作成してください。')

client_id = client_secret = ''
try:
    client_id = cnf['fitbit']['client_id']
    client_secret = cnf['fitbit']['client_secret']
except KeyError as err:
    print(f'設定 {err} が見つかりません。追加してください。')

