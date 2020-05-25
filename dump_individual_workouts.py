import requests
import json
from time import sleep
import os

LISTING_DUMP_DIR='monthly_dumps'
DETAILS_DUMP_DIR='details_dumps'

if not os.path.exists(DETAILS_DUMP_DIR):
    os.mkdir(DETAILS_DUMP_DIR)

if not 'USER_TOKEN' in os.environ:
    print('USER_TOKEN env not set')
    quit()
if not 'USER_ID' in os.environ:
    print('USER_ID env not set')
    quit()

def dump_workout(id):
    cookies = {
        'USER_TOKEN': os.environ['USER_TOKEN']
    }
    user_id = os.environ['USER_ID']
    url = f'https://www.endomondo.com/rest/v1/users/{user_id}/workouts/{id}'
    r = requests.get(url, cookies=cookies)
    return r.json()


if __name__ == '__main__':
    for year in range(2013, 2020+1):
        for month in range(1, 12+1):
            print(f'Processing {year}-{month}')
            json_location = f'{LISTING_DUMP_DIR}/{year}-{month}.json'
            if not os.path.exists(json_location):
                print(f'Location {json_location} not found, skipping...')
                continue

            with open(json_location) as fp:
                monthly_data = json.load(fp)
            for item in monthly_data['data']:
                id = item['id']
                print(f'Processing workout {id}')
                workout_json_location = f'{DETAILS_DUMP_DIR}/{year}-{month}-{id}.json'
                if os.path.exists(workout_json_location):
                    print(f'{workout_json_location} exists, skipping...')
                    continue
                workout_data = dump_workout(id)
                with open(workout_json_location, 'w') as fp:
                    json.dump(workout_data, fp)
                sleep(1)
