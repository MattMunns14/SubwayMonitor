from sms_reciever import handle_sns_event


def lambda_handler(event, context):
    print(event)
    handle_sns_event(event)
