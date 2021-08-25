import boto3
import os
import json
import time
from .utils import dict_to_dynamo_json

SUPPORTED_TRAINS_AND_DIRECTIONS = [('C', 'N'), ('C', 'S')]


def handle_sns_event(event):

    sns_client = boto3.client('sns')
    message = json.loads(event['Records'][0]['Sns']['Message'])
    message_as_tuple = tuple(message['messageBody'].split())
    number = message['originationNumber']

    if message_as_tuple in SUPPORTED_TRAINS_AND_DIRECTIONS:

        write_monitoring_request_to_dynamo(message_as_tuple, number)
        response = sns_client.publish(
            TargetArn=os.environ['SMS_SENDER_TOPIC_ARN'],
            Message=f'Monitoring the {message_as_tuple[0]} heading {message_as_tuple[1]}'
        )

    else:

        response = sns_client.publish(
            TargetArn=os.environ['SMS_SENDER_TOPIC_ARN'],
            Message=f'Message not understood or train not supported'
        )


def write_monitoring_request_to_dynamo(message_as_tuple, number):

    dynamo_client = boto3.client('dynamodb')
    request_dict = {
        'timestamp': time.time(),
        'status': 'open',
        'train': message_as_tuple[0],
        'direction': message_as_tuple[1],
        'requester': number
    }
    dynamo_client.put_item(
        Item=dict_to_dynamo_json(request_dict),
        Table=os.environ['DYNAMODB_TABLE']
    )
