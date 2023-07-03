import tornado.ioloop
import tornado.web
from app import AppHandler
from db import MongoDbConnect

MONGO_DB_NAME = 'guid-db'

def start_app(mongoClient):
    # Connect to MongoDB
    client = mongoClient.connect()
    assert client is not None, "MongoDB connection failed!!!"
    db = client[MONGO_DB_NAME]
    return tornado.web.Application([
        (r"/guid/([^/]+)/?", AppHandler, dict(db=db)),
        (r"/guid/?", AppHandler, dict(db=db)),
        (r"/.*", AppHandler, dict(db=db)),
    ])


if __name__ == "__main__":
    mongoClient = MongoDbConnect()
    try:
        print("Starting the webserver")
        app = start_app(mongoClient)
        app.listen(8081)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt as interrupt:
        mongoClient.close()
        print("\nStopping the webserver")
