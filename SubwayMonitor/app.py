import json
import os
import time

import requests as r
from google.transit import gtfs_realtime_pb2
from twilio.twiml.messaging_response import MessagingResponse


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
    print(event)
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

    response = MessagingResponse()
    response.message('Hello back')
    response = str(response)
    print(response)
    return response


def get_next_departure_for_list_of_stations(url, stations):
    response = r.get(
        url=url,
        headers=headers
    )
    for station in stations:
        next_departure_dict[station] = []

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            tu = entity.trip_update
            for stu in tu.stop_time_update:
                if stu.HasField('stop_id'):
                    if stu.stop_id in next_departure_dict:
                        next_departure_dict[stu.stop_id].append(stu.arrival.time)
