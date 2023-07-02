from pymongo import MongoClient
from urllib.parse import quote_plus
import ssl

uri = "mongodb+srv://my-first-user:Welcome123@my-first-atlas-db.qa1bd.mongodb.net/?retryWrites=true&w=majority"

# Disable SSL certificate verification by setting ssl_cert_reqs to ssl.CERT_NONE
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class MongoDbConnect:

    def __init__(self, client=None):
        self.client = client

    def connect(self):
        encoded_connection_string = quote_plus(uri)
        if not self.client:
            self.client = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True)
        return self.client

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
