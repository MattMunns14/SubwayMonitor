from sms_reciever import handle_sns_event


def lambda_handler(event, context):
    print(event)

    event_type = get_event_type(event)
    if event_type == 'SNS':
        handle_sns_event(event)


def get_event_type(event):
    if 'Records' in event:
        if event['Records'][0]['EventSource'] == 'aws:sns':
            return 'SNS'

