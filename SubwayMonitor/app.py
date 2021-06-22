import json
import os
import time

import requests as r
from google.transit import gtfs_realtime_pb2

headers = {
    'x-api-key': os.environ['API_KEY']
}


WAIT_TOLERANCE = 120

endpoints_and_stations = {
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs': {
        'stations': ['123S', '123N'],
        'time_to_station': 300
    },
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace': {
        'stations': ['A22S', 'A22N'],
        'time_to_station': 240
    }

}

next_departure_dict = {}


def lambda_handler(event, context):
    for url, data in endpoints_and_stations.items():
        get_next_departure_for_list_of_stations(url, data['stations'])

    time_now = int(time.time())

    departure_in_range_dict = {}

    for data in endpoints_and_stations.values():
        for station in data['stations']:
            if list(filter(lambda time_val: (time_val >= time_now + data['time_to_station']) and (time_val < time_now +
                                                                                                  data[
                                                                                                      'time_to_station']
                                                                                                  + WAIT_TOLERANCE),
                           next_departure_dict[station])):
                departure_in_range_dict[station] = True
            else:
                departure_in_range_dict[station] = False

    return {

            "statusCode": 200,
            "body": json.dumps(departure_in_range_dict),
        }


def get_next_departure_for_list_of_stations(url, stations):
    response = r.get(
        url=url,
        headers=headers
    )

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            tu = entity.trip_update
            for stu in tu.stop_time_update:
                if stu.HasField('stop_id'):
                    for station in stations:
                        if stu.stop_id == station:
                            if station in next_departure_dict:
                                next_departure_dict[station].append(stu.arrival.time)
                            else:
                                next_departure_dict[station] = [stu.arrival.time]


