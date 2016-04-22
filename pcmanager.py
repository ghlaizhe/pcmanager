from tornado.options import define, options
import tornado
import tornado.web
import tornado.httpserver
import os
from tornado.ioloop import PeriodicCallback

define("port", default=8888, help="run on the given port", type=int)

localDb =  [{"ip":"192.168.1.1", "status":"running", "username":"jiafzhan",
                "location":"floor 24", "pc_number":11111, "device_number":22222222},
            {"ip":"192.168.1.2", "status":"poweroff", "username":"jiafzhan",
                "location":"floor 24", "pc_number":11111, "device_number":22222222}]

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
        ]

        settings = dict(
            title = u"Pc Manager",
            template_path = os.path.join(os.path.dirname(__file__), "templates")
        )

        super(Application, self).__init__(handlers, **settings)

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
          return localDb


class HomeHandler(BaseHandler):
    def get(self):
        entries = self.db
        self.render("home.html", entries = entries)


def work():
    print "this is the callback"

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    ioloop = tornado.ioloop.IOLoop.instance()

    # background update every x seconds
    task = tornado.ioloop.PeriodicCallback(
            work,
            2 * 1000)
    task.start()

    ioloop.start()

if __name__ == "__main__":
    main()
