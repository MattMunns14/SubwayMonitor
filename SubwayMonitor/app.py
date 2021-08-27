from subway_monitor import train_in_range
from utils import dynamo_item_to_dict
import os
import boto3


def lambda_handler(event, context):
    print(event)
    event_source = get_event_source(event)
    if event_source == 'DynamoDB':
        record = event['Records'][0]
        if record['eventName'] == 'INSERT':
            new_item = dynamo_item_to_dict(record['dynamodb']['NewImage'])
            train = new_item['train']
            direction = new_item['direction']
            if train_in_range(train, direction):
                post_to_topic(train, direction)


def post_to_topic(train, direction):

    sns_client = boto3.client('sns')
    response = sns_client.publish(
        TargetArn=os.environ['SMS_SENDER_TOPIC_ARN'],
        Message=f'Leave now the {train} heading {direction}'
    )


def get_event_source(event):
    source = event['Records'][0]['eventSource']
    if source == 'aws:dynamodb':
        return 'DynamoDB'

