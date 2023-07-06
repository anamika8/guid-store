from pymongo import MongoClient
from urllib.parse import quote_plus
import ssl

uri = "mongodb+srv://my-first-user:Welcome123@my-first-atlas-db.qa1bd.mongodb.net/?retryWrites=true&w=majority"

# Helps to connect and disconnect from MongoDB Server
class MongoDbConnect:
    # constructor
    def __init__(self, client=None):
        self.client = client

    def connect(self):
        # Connects when client is none
        if not self.client:
            self.client = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True)
        return self.client

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
        print("MongoDB client closed")
