import tornado.ioloop
import tornado.web
from app import AppHandler


def start_app():
    return tornado.web.Application([
        (r"/guid/([A-Fa-f0-9]+)", AppHandler),
        (r"/", AppHandler),
    ])


if __name__ == "__main__":
    app = start_app()
    app.listen(8081)
    tornado.ioloop.IOLoop.current().start()
