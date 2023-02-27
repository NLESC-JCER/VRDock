import json
import tornado.web
import asyncio

from typing import Any
from tornado import websocket, web, ioloop, httputil



class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")


class SocketHandler(websocket.WebSocketHandler):

    def __init__(self, application: tornado.web.Application, request: httputil.HTTPServerRequest,
                 **kwargs: Any) -> None:
        super().__init__(application, request, **kwargs)

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        decoded_message = json.loads(message)
        print('message', decoded_message)
        self.write_message(json.dumps({'type': 'score', 'data': decoded_message['pos']['x']}))

    def open(self):
        print('ws open')

    def on_close(self):
        print('ws close')


app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    # (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
    # (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
])

if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.instance().start()
