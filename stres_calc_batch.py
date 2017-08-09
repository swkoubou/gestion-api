from gestion.database import session
from gestion.models import User, Stress
import configparser, os
import requests
import pandas, numpy
import base64
import argparse
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

##### コマンドライン引数の処理 #####
# 日付の指定によってクロールするデータの日付を変える
parser = argparse.ArgumentParser()
parser.add_argument('-y', '--year', type=int, help='年の指定')
parser.add_argument('-m', '--month', type=int, help='月の指定')
parser.add_argument('-d', '--day', type=int, help='日の指定')
args = parser.parse_args()

year = args.year if args.year else date.today().year
month = args.month if args.month else date.today().month
day = args.day if args.day else date.today().day
crawl_date = date(year, month, day)

##### ユーザ毎にデータを収集してストレス値の計算 #####
for user in session.query(User):
    # fitbitアカウントが登録されていない場合と、既に同じ日にちのデータが
    # 取得されている場合はクロールしない
    if user.fitbit_access_token == '' or not (session.query(Stress)
                                               .filter_by(owner_id=user.id,
                                                          date=crawl_date)):
        continue
    resource_url = f'https://api.fitbit.com/1/user/{user.fitbit_id}/activities/heart/date/{crawl_date.isoformat()}/1d/1sec/time/00:00/23:59.json'
    r = requests.get(resource_url, headers={
        'Authorization': 'Bearer ' + user.fitbit_access_token,
    })
    if r.status_code == 200:
        print('success')
        data = r.json()['activities-heart-intraday']['dataset']
        heart_rate = numpy.array([datum['value'] for datum in data])
        try:
            stress_val = float(stress_calc_package.calc(heart_rate))
        except:
            stress_val = 0
        print(stress_val)
        try:
            # stress_calc_package()の返り値の型が不定で、nanを判定できないので
            # DBにデータを入れるときにnot null制約に引っかかるのをハンドリングする
            stress = Stress(date=crawl_date.today(), stress=stress_val, owner_id=user.id)
            session.add(stress)
            session.commit()
        except Exception:
            session.rollback()
    else:
        print(f'failued code: {r.status_code}')
        print(r.text)
