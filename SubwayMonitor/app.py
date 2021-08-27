import json
import os
import time

import boto3

from subway_monitor import train_in_range
from utils import dynamo_item_to_dict

POLLING_FREQUENCY = 20


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
    else:
        pass
    if train_in_range(train, direction):
        post_to_topic_and_update_dynamo(train, direction, timestamp)
    else:
        time.sleep(POLLING_FREQUENCY)
        sqs_client = boto3.client('sqs')
        sqs_client.send_message(
            QueueUrl=os.environ['SQS_QUEUE_URL'],
            MessageBody=json.dumps({
                "train": train,
                "direction": direction,
                "timestamp": timestamp
            })
        )


def post_to_topic_and_update_dynamo(train, direction, timestamp):

    sns_client = boto3.client('sns')
    response = sns_client.publish(
        TargetArn=os.environ['SMS_SENDER_TOPIC_ARN'],
        Message=f'Leave now the {train} heading {direction}'
    )

    table = boto3.resource('dynamodb').table(os.environ['DYNAMODB_TABLE'])
    record = table.get_item(
        Key={'timestamp': timestamp}
    )
    record['status'] = 'closed'
    table.put_item(
        Item=record
    )


def get_event_source(event):
    source = event['Records'][0]['eventSource']
    if source == 'aws:dynamodb':
        return 'DynamoDB'
    if source == 'aws:sqs':
        return 'SQS'

