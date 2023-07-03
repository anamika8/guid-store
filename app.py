import tornado.web
import json
from generate import RandomGUIDGenerator

COLLECTION_NAME = "guids"
class AppHandler(tornado.web.RequestHandler):

    def initialize(self, db):
        self.db_client = db

    def get(self, guid=None):
        if guid is None:
            self.write("Welcome to guid-store\n")
        else:
            self.get_guid(guid)

    def get_guid(self, guid):
        collection = self.db_client[COLLECTION_NAME]
        self.guid_already_present(collection, guid)

    def post(self, guid=None):
        collection = self.db_client[COLLECTION_NAME]
        data = json.loads(self.request.body.decode('utf-8'))
        if guid:
            print("Received POST request for GUID: ", guid)
            self.create_guid(collection, data, guid)
        else:
            print("Creating a system-generated guid")
            self.create_guid(collection, data)

    def guid_already_present(self, collection, guid):
        result = collection.find({"guid": guid})
        if result and len(list(result)) > 0:
            print("Found guid - ", guid)
            return True
        else:
            print("Did not find guid - ", guid)
            return False

    def create_guid(self, collection, data, guid=None):
        if not guid:
            while True:
                new_guid = RandomGUIDGenerator.generate()
                guid_exists = self.guid_already_present(collection, new_guid)
                if not guid_exists:
                    break
        else:
            new_guid = guid
            if self.guid_already_present(collection, new_guid):
                self.write(f"guid - {new_guid} already exists")
                return
        data["guid"] = new_guid
        # mongo-db call
        added_guid = collection.insert_one(data)
        inserted_id = added_guid.inserted_id
        data["_id"] = str(inserted_id)  # Convert ObjectId to string
        print(f"Created a new guid - \n {data}")
        self.write(json.dumps(data))