import tornado.web

COLLECTION_NAME = "guids"
class AppHandler(tornado.web.RequestHandler):

    def initialize(self, db):
        self.db_client = db

    def get(self, *args, **kwargs):
        if args:
            guid = args[0]
            self.get_guid(guid)
        else:
            collection = self.db_client[COLLECTION_NAME]
            result = collection.find({})
            self.write("Welcome to guid-store")
            if result:
                self.write("Listing all GUIDs")
                for doc in result:
                    print(doc)
                    self.write(doc)
            else:
                self.write("guid-store is empty right now")

    def get_guid(self, guid):
        self.write("guid-store is empty right now")