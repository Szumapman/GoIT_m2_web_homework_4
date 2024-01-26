import json
import mimetypes
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import os
import threading
import logging


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value
            for key, value in [item.split("=") for item in data_parse.split("&")]
        }
        byte_data = json.dumps(data_dict).encode()
        run_socket_client("127.0.0.1", 5000, byte_data)
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
            if Path().joinpath(parse_result.path[1:]).exists():
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


def run_socket_server(ip, port, data_dict, data_path):
    logging.debug("starting socket server ...")
    data_to_save = b""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            if data == b"END_OF_FORM":
                save_json_data(data_dict, data_to_save, data_path)
                data_to_save = b""
            else:
                data_to_save += data
    except KeyboardInterrupt:
        logging.debug(f"Destroy socket server")
    finally:
        logging.debug(f"finally Destroy socket server")
        sock.close()


def save_json_data(data_dict, data, data_path):
    data_dict[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = json.loads(data)
    with open(data_path, "w") as f:
        json.dump(data_dict, f)


def run_socket_client(host, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        data_chunks = [data[i : i + 1024] for i in range(0, len(data), 1024)]
        for data_chunk in data_chunks:
            sock.sendto(data_chunk, (host, port))
        sock.sendto(b"END_OF_FORM", (host, port))


def run_http_server(
    server_class=HTTPServer, handler_class=HttpHandler, ip="127.0.0.1", port=3000
):
    server_address = (ip, port)
    http_server = server_class(server_address, handler_class)
    logging.debug("Starting httpd...")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        logging.debug(f"Destroy http server")
        http_server.server_close()


def main():
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")
    storage_path = Path(__file__).parent.absolute().joinpath("storage")
    data_path = storage_path.joinpath("data.json")
    if not storage_path.exists():
        Path.mkdir(Path(__file__).parent.absolute().joinpath("storage"))
    if not data_path.exists():
        Path.touch(data_path)
    if os.path.getsize(data_path) == 0:
        data_dict = {}
    else:
        with open(data_path, "r") as f:
            data_dict = json.load(f)
    http_server = threading.Thread(target=run_http_server)
    socket_server = threading.Thread(
        target=run_socket_server, args=("127.0.0.1", 5000, data_dict, data_path)
    )
    socket_server.start()
    http_server.start()
    socket_server.join()
    http_server.join()
    logging.debug("Destroy all threads")


if __name__ == "__main__":
    main()
