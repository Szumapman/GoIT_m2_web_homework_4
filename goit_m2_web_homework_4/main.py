import json
import mimetypes
import pathlib
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse


data_json = {}
class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        key = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value
            for key, value in [item.split("=") for item in data_parse.split("&")]
        }
        print(f"data_dict: {data_dict}")
        byte_data = json.dumps(data_dict).encode()
        # run_socket_client("127.0.0.1", 5000, byte_data)
        self.send_response(302)
        self.send_header("Location", "templates/index.html")
        self.end_headers()

    def do_GET(self):

        parse_result = urllib.parse.urlparse(self.path)
        if parse_result.path == "/":
            self.send_html_file("./templates/index.html")
        elif parse_result.path == "/message.html":
            self.send_html_file("./templates/message.html")
        else:
            if pathlib.Path().joinpath(parse_result.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("templates/error.html", 404)

    def send_html_file(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        with open(filename, "rb") as f:
            self.wfile.write(f.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-Type", mt[0])
        else:
            self.send_header("Content-Type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler, port=3000):
    server_address = ("0.0.0.0", port)
    http = server_class(server_address, handler_class)
    print("Starting httpd...")
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
