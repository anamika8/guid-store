import json
import boto3
import redis
import os
from util import GuidUtil
from typing import Any

# DynamoDB and Redis initialization using environment variables
dynamodb = boto3.resource('dynamodb')
table_name = 'GUIDStore'    
table = dynamodb.Table(table_name)

# redis_client = redis.StrictRedis.from_url(f"redis://{os.environ['REDIS_ENDPOINT']}")
redis_client = redis.StrictRedis.from_url('redis://guidcache-qgk9x0.serverless.use2.cache.amazonaws.com:6379')

# Constants
FIELD_EXPIRE = "expire"
FIELD_GUID = "guid"
CACHE_EXPIRATION_SECS = 600  # 10 minutes

class ObjectIdEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def lambda_handler(event, context):
    print("Lambda function invoked")
    print("Received event:", json.dumps(event))
    # Parse HTTP method and path
    http_method = event['requestContext']['http']['method']
    path = event['rawPath']

    # Handle POST request for creating a new GUID
    if http_method == 'POST':
        if path == '/guid':  # POST /guid
            data = json.loads(event['body'])
            return create_guid(data)
        elif '/guid/' in path:  # POST /guid/{guid} for updating a specific GUID
            guid = path.split('/')[-1]
            data = json.loads(event['body'])
            return update_guid(guid, data)

    # Handle GET request to retrieve a GUID or list all GUIDs
    elif http_method == 'GET':
        if path == '/guid':  # GET /guid without specifying a GUID
            # Return a welcome message or list all GUIDs
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Welcome to GUID Store'})
            }
            # Optionally, uncomment the line below to list all GUIDs
            # return list_all_guids()
        elif '/guid/' in path:  # GET /guid/{guid} to retrieve a specific GUID
            guid = path.split('/')[-1]
            return get_guid(guid)
        else:
            print("Error: Unable to consume the request")

    # Handle PUT request to update metadata for a GUID
    elif http_method == 'PUT' and '/guid/' in path:
        guid = path.split('/')[-1]
        data = json.loads(event['body'])
        return update_guid(guid, data)

    # Handle DELETE request to delete a GUID
    elif http_method == 'DELETE' and '/guid/' in path:
        guid = path.split('/')[-1]
        return delete_guid(guid)

    print("ERROR: Did not match expected paths")
    return {
        'statusCode': 400,
        'body': json.dumps({'message': 'Invalid request'})
    }

# Helper function to create a GUID in DynamoDB
def create_guid(data, guid=None):
    # Generate a unique GUID if none is provided
    if not guid:
        guid = GuidUtil.generate_random_guid()
    data[FIELD_GUID] = guid

    # Validate and set expiration if not provided
    if FIELD_EXPIRE not in data:
        data[FIELD_EXPIRE] = GuidUtil.generate_expiration_time()
    print("inserting into dynamodb")
    # Insert into DynamoDB
    table.put_item(Item=data)
    print("inserting into REdis")
    # Cache the GUID in Redis
    #add_to_cache(guid, data)
    
    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'GUID created', 'guid': guid, 'data': data})
    }

# Helper function to get GUID information
def get_guid(guid):
    # Check Redis cache first
  
    cache_result = redis_client.get(guid)
    if cache_result:
        cache_data = json.loads(cache_result.decode('utf-8'))
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Retrieved from cache', 'guid': guid, 'data': cache_data})
        }
 
    # Retrieve from DynamoDB if not cached
    response = table.get_item(Key={FIELD_GUID: guid})
    if 'Item' in response:
        data = response['Item']
        # Cache the result in Redis
        #add_to_cache(guid, data)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'GUID retrieved', 'guid': guid, 'data': data})
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'GUID not found'})
        }

# Helper function to update GUID metadata
def update_guid(guid, data):
    # Update DynamoDB item
    table.update_item(
        Key={FIELD_GUID: guid},
        UpdateExpression="SET expire = :expire, user = :user",
        ExpressionAttributeValues={
            ':expire': data.get('expire'),
            ':user': data.get('user')
        }
    )
    # Update Redis cache
    #add_to_cache(guid, data)
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'GUID updated', 'guid': guid, 'data': data})
    }

# Helper function to delete a GUID from DynamoDB and Redis
def delete_guid(guid):
    # Delete from DynamoDB
    table.delete_item(Key={FIELD_GUID: guid})
    # Remove from Redis cache
    redis_client.delete(guid)
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'GUID deleted', 'guid': guid})
    }

# Helper function to add data to Redis cache
def add_to_cache(guid, data):
    redis_client.setex(guid, CACHE_EXPIRATION_SECS, json.dumps(data))

# Optional: Function to list all GUIDs (Use with caution for large datasets)
def list_all_guids():
    # Scan operation to retrieve all items in the DynamoDB table
    response = table.scan()
    items = response.get('Items', [])
    return {
        'statusCode': 200,
        'body': json.dumps({'guids': items})
    }

