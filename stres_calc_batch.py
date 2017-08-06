from gestion.database import session
from gestion.models import User, Stress
import configparser, os
import requests
import pandas, numpy
import base64
import stress_calc_package
from datetime import date

BASE_DIR = os.path.abspath('.')

##### Fitbit開発者用トークンの取得 #####
cnf = configparser.ConfigParser()
if cnf.read(os.path.join(BASE_DIR, 'gestion/config/system.cnf')) == []:
    print('設定ファイルが見つかりません。config/system.cnfを作成してください。')

client_id = client_secret = ''
try:
    client_id = cnf['fitbit']['client_id']
    client_secret = cnf['fitbit']['client_secret']
except KeyError as err:
    print(f'設定 {err} が見つかりません。追加してください。')


##### ユーザ毎にデータを収集してストレス値の計算 #####
for user in session.query(User):
    if user.fitbit_access_token == '':
        continue
    resource_url = f'https://api.fitbit.com/1/user/{user.fitbit_id}/activities/heart/date/2017-01-28/1d/1sec/time/00:00/23:59.json'
    r = requests.get(resource_url, headers={
        'Authorization': 'Bearer ' + user.fitbit_access_token,
    })
    if r.status_code == 200:
        print('success')
        data = r.json()['activities-heart-intraday']['dataset']
        heart_rate = numpy.array([datum['value'] for datum in data])
        stress_val = float(stress_calc_package.calc(heart_rate))
        print(stress_val)
        stress = Stress(date=date.today(), stress=stress_val, owner_id=user.id)
        session.add(stress)
        session.commit()
    else:
        print('failued')
