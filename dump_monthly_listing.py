import requests
import json
from datetime import datetime
from time import sleep
from dateutil.relativedelta import  relativedelta
import os

DUMP_DIR='monthly_dumps'

if not 'USER_TOKEN' in os.environ:
    print('USER_TOKEN env not set')
    quit()
if not 'USER_ID' in os.environ:
    print('USER_ID env not set')
    quit()

if not os.path.exists(DUMP_DIR):
    os.mkdir(DUMP_DIR)

def dump_month(year, month):
    print(f'Dumping for: {year}-{month}')
    begin_time = datetime(year=year, month=month, day=1)
    end_time = begin_time + relativedelta(months=1)
    # end_time = datetime(year=year, month=month+1, day=1)
    begin_time_str = datetime.strftime(begin_time, '%Y-%m-01T00:00:00.000Z')
    end_time_str = datetime.strftime(end_time, '%Y-%m-01T00:00:00.000Z')
    print('times', begin_time_str, end_time_str)
    cookies = {
        'USER_TOKEN': os.environ['USER_TOKEN']
    }
    user_id = os.environ['USER_ID']
    url = f'https://www.endomondo.com/rest/v1/users/{user_id}/workouts?before={end_time_str}&after={begin_time_str}'
    r = requests.get(url, cookies=cookies)
    print(r)
    print(r.status_code)
    return r.json()

if __name__ == '__main__':
    for year in range(2013, 2020+1):
        for month in range(1, 12+1):
            month_data = {
                'year': year,
                'month': month,
                'data': dump_month(year, month)
            }
            with open(f'{DUMP_DIR}/{year}-{month}.json', 'w') as fp:
                json.dump(month_data, fp)
            sleep(1)