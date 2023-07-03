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
        self.write("guid-store is empty right now")

    def post(self, guid=None):
        collection = self.db_client[COLLECTION_NAME]
        if guid:
            self.write("Received POST request for GUID: " + guid + "\n")
        else:
            print("Creating a system-generated guid")
            new_guid = RandomGUIDGenerator.generate()
            data = json.loads(self.request.body.decode('utf-8'))
            data["guid"] = new_guid
            added_guid = collection.insert_one(data)
            inserted_id = added_guid.inserted_id
            data["_id"] = str(inserted_id)  # Convert ObjectId to string
            print(f"Created a new guid - \n {data}")
            self.write(json.dumps(data))
