from boto3.dynamodb.types import TypeDeserializer, TypeSerializer


def dict_to_dynamo_json(input_dict):
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in input_dict.items()}


def dynamo_item_to_dict(dynamo_item):
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_item.items()}
