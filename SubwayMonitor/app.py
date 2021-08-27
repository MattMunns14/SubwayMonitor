from subway_monitor import poll_trains


def lambda_handler(event, context):
    print(event)
    poll_trains(event)

