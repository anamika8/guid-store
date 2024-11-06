import boto3

def save_guid(table, guid):
    # Function to save GUID in DynamoDB
    table.put_item(Item={'guid': guid})

def get_guid(table, guid):
    # Function to retrieve GUID from DynamoDB
    response = table.get_item(Key={'guid': guid})
    return response.get('Item')

