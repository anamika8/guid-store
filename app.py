import json
import boto3
import redis
from db import get_guid, save_guid  # Assuming these functions interact with DynamoDB
from util import generate_guid  # Assuming util has a GUID generation function

# Initialize DynamoDB client and Redis client using environment variables
dynamodb = boto3.resource('dynamodb')
table_name = 'GUIDStore'  
table = dynamodb.Table(table_name)

redis_client = redis.StrictRedis.from_url('guidcache-qgk9x0.serverless.use2.cache.amazonaws.com:6379')  

def lambda_handler(event, context):
    # Parse HTTP method and route from API Gateway event
    http_method = event['httpMethod']
    path = event['path']

    if http_method == 'POST' and path == '/guid':
        # Generate a new GUID and save it to DynamoDB
        new_guid = generate_guid()
        save_guid(table, new_guid)

        # Cache the GUID in Redis
        redis_client.set(new_guid, json.dumps({"cached": True}))
        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'GUID created', 'guid': new_guid})
        }

    elif http_method == 'GET' and '/guid/' in path:
        guid = path.split('/')[-1]
        
        # Check Redis cache first
        cached_guid = redis_client.get(guid)
        if cached_guid:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'GUID retrieved from cache', 'guid': guid})
            }

        # Retrieve from DynamoDB if not cached
        guid_data = get_guid(table, guid)
        if guid_data:
            redis_client.set(guid, json.dumps(guid_data))  # Cache for future requests
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'GUID retrieved', 'guid': guid_data})
            }

        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'GUID not found'})
        }

    return {
        'statusCode': 400,
        'body': json.dumps({'message': 'Invalid request'})
    }
