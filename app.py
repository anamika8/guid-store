import tornado.web

class AppHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        if args:
            guid = args[0]
            self.get_guid(guid)
        else:
            print("in here")
            self.write("Welcome to guid-store")


    def get_guid(self, guid):
        self.write("guid-store is empty right now")