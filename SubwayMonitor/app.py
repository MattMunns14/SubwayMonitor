import json
import os
import time

import boto3

from subway_monitor import train_in_range
from utils import dynamo_item_to_dict
from decimal import Decimal

POLLING_FREQUENCY = 15


def lambda_handler(event, context):
    print(event)
    event_source = get_event_source(event)
    record = event['Records'][0]
    if event_source == 'DynamoDB':
        if record['eventName'] == 'INSERT':
            new_item = dynamo_item_to_dict(record['dynamodb']['NewImage'])
            train = new_item['train']
            direction = new_item['direction']
            timestamp = new_item['timestamp']
            if train_in_range(train, direction):
                post_to_topic(train, direction, timestamp)
                update_dynamo(timestamp, 'notified')
            else:
                post_to_queue(train, direction, timestamp)
    else:
        body = json.loads(record['body'])
        train = body['train']
        direction = body['direction']
        timestamp = body['timestamp']

        if time.time() - float(timestamp) >= 2700:
            update_dynamo(timestamp, 'expired')

        elif train_in_range(train, direction):
            post_to_topic(train, direction, timestamp)
            update_dynamo(timestamp, 'notified')
        else:
            post_to_queue(train, direction, timestamp)


def post_to_queue(train, direction, timestamp):
    time.sleep(POLLING_FREQUENCY)
    sqs_client = boto3.client('sqs')
    sqs_client.send_message(
        QueueUrl=os.environ['SQS_QUEUE_URL'],
        MessageBody=json.dumps({
            "train": train,
            "direction": direction,
            "timestamp": float(timestamp)
        })
    )


def post_to_topic(train, direction, timestamp):

    sns_client = boto3.client('sns')
    response = sns_client.publish(
        TargetArn=os.environ['SMS_SENDER_TOPIC_ARN'],
        Message=f'Leave now for the {train} heading {direction}'
    )


def get_event_source(event):
    source = event['Records'][0]['eventSource']
    if source == 'aws:dynamodb':
        return 'DynamoDB'
    if source == 'aws:sqs':
        return 'SQS'


def update_dynamo(timestamp, status):
    if not isinstance(timestamp, Decimal):
        timestamp = Decimal(timestamp)
    table = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_TABLE'])
    record = table.get_item(
        Key={'timestamp': timestamp}
    )
    record['status'] = status
    table.put_item(
        Item=record
    )

