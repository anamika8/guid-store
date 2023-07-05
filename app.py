from typing import Any
import tornado.web
import json
from util import GuidUtil
from bson import ObjectId

COLLECTION_NAME = "guids"
FIELD_EXPIRE = "expire"
FIELD_GUID = "guid"
CACHE_EXPIRATION_SECS = 600 # 10 minutes

# Helps print the GET /guid/{guid} result
class ObjectIdEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

class AppHandler(tornado.web.RequestHandler):

    def initialize(self, db, redis_client):
        self.db_client = db
        self.redis_client = redis_client

    def get(self, guid=None):
        if guid is None:
            self.write("Welcome to guid-store\n")
        else:
            self.get_guid(guid)

    def get_guid(self, guid):
        # first check in cache
        cache_result = self.redis_client.get(guid)
        if cache_result:
            print(f"Found {guid} in cache")
            cache_data = json.loads(cache_result.decode('utf-8'))
            self.write(cache_data)
            return
        collection = self.db_client[COLLECTION_NAME]
        result = collection.find_one({"guid": guid})
        if result and len(list(result)) > 0:
            print("Found guid - ", guid)
            json_result = json.dumps(result, cls=ObjectIdEncoder)
            # since it is not available in cache, store it
            self.add_to_cache(guid, json_result)
            self.write(json_result)
        else:
            print("Did not find guid - ", guid)
            self.write({})

    def post(self, guid=None):
        collection = self.db_client[COLLECTION_NAME]
        data = json.loads(self.request.body.decode('utf-8'))

        if guid:
            print("Received POST request for GUID: ", guid)
            self.create_guid(collection, data, guid)
        else:
            print("Creating a system-generated guid")
            self.create_guid(collection, data)


    def put(self, guid=None):
        collection = self.db_client[COLLECTION_NAME]
        data = json.loads(self.request.body.decode('utf-8'))
        if guid:
            print("Received PUT request for GUID: ", guid)
            # perform data input validation
            error_msg = self.input_data_validation(data, guid)
            if error_msg != "":
                self.send_user_error_message(error_msg)
                return
            #checks if guid is present in datastore    
            if not self.guid_already_present(collection, guid):
                self.send_user_error_message(f"guid - {guid} is not available in data store")
                return
            filter = {"guid": guid}
            update_operation = {"$set": data}
            result = collection.update_one(filter, update_operation)
            print("Document updated successfully.")
            self.update_cache(guid, "update", collection)
            self.write(data)
        else:
            self.send_user_error_message("Need to provide guid like '/guid/{guid}' for PUT request")

    def delete(self, guid=None):
        collection = self.db_client[COLLECTION_NAME]
        if guid:
            print("Received DELETE request for GUID: ", guid)
            result = collection.delete_one({"guid": guid})
            if result.deleted_count == 1:
                print("Document deleted successfully.")
                self.update_cache(guid, "delete", collection)
                self.write("")
            else:
                self.send_user_error_message(f"guid - {guid} is not available in data store")
                return
        else:
            self.send_user_error_message("Need to provide guid like '/guid/{guid}' for DELETE request")

    def guid_already_present(self, collection, guid):
        result = collection.find({"guid": guid})
        if result and len(list(result)) > 0:
            print("Found guid - ", guid)
            return True
        else:
            print("Did not find guid - ", guid)
            return False
        
    def send_user_error_message(self, usr_error_msg):
        self.set_status(400)
        self.write(usr_error_msg)
        
    # does user input validation before POST/ PUT
    def input_data_validation(self, input_data, guid):
        if FIELD_GUID in input_data:
            return "The GUID itself should not be part of the payload"
        
        if not GuidUtil.is_hex(guid):
            return "Provided guid is in incorrect format"
            
        if FIELD_EXPIRE in input_data:
            if not GuidUtil.is_time_format_correct(input_data[FIELD_EXPIRE]):
                return "expire field should be formatted in Unix time"
            if GuidUtil.is_expired_time(input_data[FIELD_EXPIRE]):
                return "expire field value should be greater than current time"
        return ""

    def create_guid(self, collection, data, guid=None):
        if not guid:
            # generate a unique random guid if not provided
            while True:
                new_guid = GuidUtil.generate_random_guid()
                guid_exists = self.guid_already_present(collection, new_guid)
                if not guid_exists:
                    break
        else:
            new_guid = guid
            if self.guid_already_present(collection, new_guid):
                # send error message if duplicate guid is used
                self.set_status(400)
                self.write(f"guid - {new_guid} already exists")
                return
        
        # perform data input validation
        error_msg = self.input_data_validation(data, new_guid)
        if error_msg != "":
            self.send_user_error_message(error_msg)
            return

        data[FIELD_GUID] = new_guid
        # generate unix formatted expiration time if not provided
        if FIELD_EXPIRE not in data:
            data[FIELD_EXPIRE] = GuidUtil.generate_expiration_time()
        # mongo-db call
        added_guid = collection.insert_one(data)
        inserted_id = added_guid.inserted_id
        data["_id"] = str(inserted_id)  # Convert ObjectId to string
        print(f"Created a new guid - \n {data}")
        self.add_to_cache(new_guid, data)
        self.write(json.dumps(data))

    def add_to_cache(self, cache_key, value:dict):
        # convert dict value to bytes for storing
        encode_data = json.dumps(value, indent=2).encode('utf-8')
        # store in cache
        self.redis_client.setex(cache_key, CACHE_EXPIRATION_SECS, encode_data)
        print(f"Added {cache_key} to Redis cache")

    def update_cache(self, cache_key, operation, collection):
        if operation == "delete":
            # delete from cache
            result = self.redis_client.delete(cache_key)
            if result == 1:
                print(f"Key '{cache_key}' successfully removed from the Redis cache.")
            else:
                print(f"Key '{cache_key}' does not exist in the Redis cache.")
        else:
            result = collection.find_one({"guid": cache_key})
            if result and len(list(result)) > 0:
                print(f"Updating the cache with the modified value from database")
                json_result = json.dumps(result, cls=ObjectIdEncoder)
                encode_data = json.dumps(json_result, indent=2).encode('utf-8')
                # update in cache
                self.redis_client.setex(cache_key, CACHE_EXPIRATION_SECS, encode_data)