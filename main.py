import tornado.ioloop
import tornado.web
from app import AppHandler
from db import MongoDbConnect

MONGO_DB_NAME = 'guid-db'

def start_app():
    # Connect to MongoDB
    mongoClient = MongoDbConnect()
    client = mongoClient.connect()
    assert client is not None, "MongoDB connection failed!!!"
    db = client[MONGO_DB_NAME]
    return tornado.web.Application([
        (r"/", AppHandler, dict(db=db)),
        (r"/guid/(.*)", AppHandler, dict(db=db)),
    ])


if __name__ == "__main__":
    app = start_app()
    app.listen(8081)
    tornado.ioloop.IOLoop.current().start()
