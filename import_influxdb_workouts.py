from influxdb import InfluxDBClient
import os
import json
from datetime import datetime

INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUX_DB = 'endomondo-workouts'
DETAILS_DUMP_DIR='details_dumps'

SPORT_MAP = {
    21: "Cycling (Indoor)",
    2: "Cycling (Sport)",
    1: "Cycling (Transport)",
    15: "Golfing",
    16: "Hiking",
    9: "Kayaking",
    10: "Kite surfing",
    3: "Mountain biking",
    17: "Orienteering",
    19: "Riding",
    4: "Roller skating",
    5: "Roller skiing",
    11: "Rowing",
    0: "Running",
    12: "Sailing",
    6: "Skiing (Cross country)",
    7: "Skiing (Downhill)",
    8: "Snowboarding",
    20: "Swimming",
    18: "Walking",
    14: "Walking (Fitness)",
    13: "Windsurfing",
    22: "Other",
    23: "Aerobics",
    24: "Badminton",
    25: "Baseball",
    26: "Basketball",
    27: "Boxing",
    104: "Canicross",
    87: "Circuit Training",
    93: "Climbing",
    28: "Climbing stairs",
    29: "Cricket",
    31: "Dancing",
    30: "Elliptical training",
    32: "Fencing",
    99: "Floorball",
    33: "Football (American)",
    34: "Football (Rugby)",
    35: "Football (Soccer)",
    49: "Gymnastics",
    36: "Handball",
    37: "Hockey",
    100: "Ice skating",
    95: "Kick scooter",
    48: "Martial arts",
    105: "Paddle tennis",
    106: "Paragliding",
    38: "Pilates",
    39: "Polo",
    102: "Rope jumping",
    98: "Rowing (indoors)",
    88: "Running (Treadmill)",
    40: "Scuba diving",
    89: "Skateboarding",
    101: "Ski Touring",
    91: "Snowshoeing",
    41: "Squash",
    96: "Stand Up Paddling",
    50: "Step counter",
    103: "Stretching",
    90: "Surfing",
    42: "Table tennis",
    43: "Tennis",
    97: "Trail Running",
    44: "Volleyball (Beach)",
    45: "Volleyball (Indoor)",
    94: "Walking (Treadmill)",
    46: "Weight training",
    92: "Wheelchair",
    47: "Yoga",
}

client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT)

# reset db
client.drop_database(INFLUX_DB)
client.create_database(INFLUX_DB)

idx = 0
batch = []
batch_location = []
good_gps_files = {}

for (dirpath, dirnames, filenames) in os.walk(DETAILS_DUMP_DIR):
    print('Num files to import:', len(filenames))
    for filename in filenames:
        with open(DETAILS_DUMP_DIR + '/' + filename) as fp:
            workout = json.load(fp)
        idx += 1
        if idx % 10 == 0:
            print(f'Progress: {idx}/{len(filenames)}', end='\r')
        dt = datetime.strptime(workout['start_time'], '%Y-%m-%dT%H:%M:%S.000Z')

        body = {
            'measurement': 'workouts',
            'time': workout['start_time'],
            'tags': {
                'sport': SPORT_MAP[workout['sport']],
                'month': dt.strftime('%m'),
                'month_name': dt.strftime('%B'),
                'year': dt.strftime('%Y'),
                'year_month': dt.strftime('%Y') + '-' + dt.strftime('%m'),
                'weekday': dt.strftime('%w'),
            },
            'fields': {
                'distance_m': workout['distance'] * 1000,
                'duration_s': workout['duration']
            }
        }
        additional_fields = ['heart_rate_avg', 'heart_rate_max', 'hydration', 'speed_avg', 'speed_max', 'calories']
        for field in additional_fields:
            if field in workout:
                body['fields'][field] = workout[field]
        batch.append(body)

        # WARNING: Endomondo is no longer storing GPX data in this format since 2015 :(
        # We need to export individual GPX files
        if 'points' in workout and 'points' in workout['points']:
            print(f'Browsing gps in {filename}')
            for i, item in enumerate(workout['points']['points']):
                if 'latitude' not in item:
                    continue

                time = item['time'] if 'time' in item else workout['start_time']
                body = {
                    'measurement': 'location',
                    'time': time,
                    'tags': {
                        'sport': SPORT_MAP[workout['sport']],
                    },
                    'fields': {
                        'latitude': item['latitude'],
                        'longitude': item['longitude']
                    }
                }
                batch_location.append(body)
                if filename not in good_gps_files:
                    good_gps_files[filename] = 1
# good_gps_files = list(good_gps_files.keys())
# good_gps_files.sort()
# print('Good GPS files', good_gps_files)

print(f'Batch prepared, writing {len(batch)} records...')
client.write_points(batch, database=INFLUX_DB)
print(f'Batch location writing {len(batch_location)} records...')
client.write_points(batch_location, database=INFLUX_DB)