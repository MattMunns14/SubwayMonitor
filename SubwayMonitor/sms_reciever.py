import boto3
import os
import json

SUPPORTED_TRAINS_AND_DIRECTIONS = [('C', 'N'), ('C', 'S')]


def handle_sns_event(event):

    sns_client = boto3.client('sns')

    message = json.loads(event['Records'][0]['Sns']['Message'])['messageBody']
    message_as_tuple = tuple(message.split())
    if message_as_tuple in SUPPORTED_TRAINS_AND_DIRECTIONS:
        write_monitoring_request_to_dynamo(message_as_tuple)
        response = sns_client.publish(
            TargetArn=os.environ['SMS_SENDER_TOPIC_ARN'],
            Message=f'Monitoring the {message_as_tuple[0]} heading {message_as_tuple[1]}'
        )

    else:

        response = sns_client.publish(
            TargetArn=os.environ['SMS_SENDER_TOPIC_ARN'],
            Message=f'Message not understood or train not supported'
        )


def write_monitoring_request_to_dynamo(message_as_tuple):
    pass