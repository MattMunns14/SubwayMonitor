import time
import os
import requests as r
from google.transit import gtfs_realtime_pb2

headers = {
    # 'x-api-key': os.environ['API_KEY']
    'x-api-key': 'ed2USiPGcJ9qHmZdvNjvy5byWEIViM170TIUhwph'
}

WAIT_TOLERANCE = 180


STATION_INFO = {
    'A22N': {
        'endpoint': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace',
        'time_to_station': 240
    },
    'A22S': {
        'endpoint': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace',
        'time_to_station': 240
    },
    '123S': {
        "endpoint": 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',
        'time_to_station': 300
    },
    '123N': {
        "endpoint": 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',
        'time_to_station': 300
    }

}

SUPPORTED_TRAINS_AND_INFO = {
    ('C', 'N'): {
        'station': 'A22N',
        'train': 'C'
    },
    ('C', 'S'): {
        'station': 'A22S',
        'train': 'C'
    }
}


def poll_trains(event):
    event = ('C', 'N')
    station = SUPPORTED_TRAINS_AND_INFO[event]["station"]
    url = STATION_INFO[station]['endpoint']
    train = event[0]

    time_to_station = STATION_INFO[station]['time_to_station']

    departures = get_next_departure_for_train(url, station, train)

    time_now = int(time.time())
    if list(filter(lambda time_val: (time_val >= time_now + time_to_station) and (time_val < time_now + time_to_station
                                                                                  + WAIT_TOLERANCE), departures)):
        print('In Range')
        return True
    else:
        return False


def get_next_departure_for_train(url, station, train):
    response = r.get(
        url=url,
        headers=headers
    )
    departures = []

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            tu = entity.trip_update
            for stu in tu.stop_time_update:
                if stu.HasField('stop_id'):
                    if (stu.stop_id == station) & (tu.trip.route_id == train):
                        departures.append(stu.arrival.time)
    return departures


poll_trains(1)
