import tornado.ioloop
import tornado.web
from app import AppHandler
from db import MongoDbConnect
import redis

MONGO_DB_NAME = 'guid-db'
REDIS_PW = 'hYwGwFgtNT9Ac1h9CnhnzOwovBG0SQ3r'

def start_app(mongoClient):
    # Connect to MongoDB
    client = mongoClient.connect()
    assert client is not None, "MongoDB connection failed!!!"
    db = client[MONGO_DB_NAME]
    # Connect to Redis
    redis_client = redis.Redis(
        host='redis-18436.c275.us-east-1-4.ec2.cloud.redislabs.com',
        port=18436,
        password=REDIS_PW)
    return tornado.web.Application([
        (r"/guid/([^/]+)/?", AppHandler, dict(db=db, redis_client=redis_client)),
        (r"/.*", AppHandler, dict(db=db, redis_client=redis_client)),
    ])


if __name__ == "__main__":
    # Initialize Mongo Client 
    mongoClient = MongoDbConnect()
    try:
        print("Starting the webserver")
        app = start_app(mongoClient)
        app.listen(8081)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt as interrupt:
        mongoClient.close()
        print("\nStopping the webserver")
