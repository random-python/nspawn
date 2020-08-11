import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

TESTER_SERVER_DIR = "/tmp/nspawn.tester-server"


class HttpHandler(SimpleHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=TESTER_SERVER_DIR, **kwargs)
    
    def do_PUT(self):
        path = self.translate_path(self.path)
        if path.endswith('/'):
            self.send_response(405, "Method Not Allowed")
        else:
            base_path = os.path.join(TESTER_SERVER_DIR, path)
            os.makedirs(os.path.dirname(base_path), exist_ok=True)
            length = int(self.headers['Content-Length'])
            with open(base_path, 'wb') as file:
                file.write(self.rfile.read(length))
            self.send_response(201, "Created")
        self.end_headers()


class HttpServer(threading.Thread):
    server = None
    
    def __init__(self, addr="127.0.0.1", port=8888):
        super().__init__()
        addr_port = (addr, port)
        self.server = HTTPServer(addr_port, HttpHandler)
        self.setDaemon(True)
    
    def execute_unit(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.join()
