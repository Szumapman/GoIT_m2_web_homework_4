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
from http import HTTPStatus


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value
            for key, value in [item.split("=") for item in data_parse.split("&")]
        }
        byte_data = json.dumps(data_dict).encode()
        run_socket_client("0.0.0.0", 5000, byte_data)
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", "templates/index.html")
        self.end_headers()

    def do_GET(self):
        parse_result = urllib.parse.urlparse(self.path)
        if parse_result.path == "/":
            self.send_html_file("templates/index.html")
        elif parse_result.path == "/message.html":
            self.send_html_file("templates/message.html")
        else:
            if Path().joinpath(parse_result.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file(
                    "/templates/error.html",
                    HTTPStatus.NOT_FOUND,
                )

    def send_html_file(self, filename, status_code=HTTPStatus.OK):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        with open(filename, "rb") as f:
            self.wfile.write(f.read())

    def send_static(self):
        self.send_response(HTTPStatus.OK)
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
            logging.debug(f"Received data from {address}: {data}")
            if data == b"END_OF_FORM":
                save_json_data(data_dict, data_to_save, data_path)
                data_to_save = b""
            elif data == b"STOP_SOCKET_SERVER":
                logging.debug(f"Stop socket server {data}")
                break
            else:
                data_to_save += data
    finally:
        logging.debug(f"Destroy socket server")
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


httpd = HTTPServer(("0.0.0.0", 3000), HttpHandler)


def run_http_server():
    # def run_http_server(
    #     server_class=HTTPServer, handler_class=HttpHandler, ip="0.0.0.0", port=3000
    # ):
    # server_address = (ip, port)
    logging.debug("Starting httpd...")
    # httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    finally:
        logging.debug(f"Destroy http server ")
        httpd.server_close()


def set_data_directory():
    app_directory = Path(__file__).parent.absolute()
    storage_directory_path = app_directory.joinpath("storage")
    if not storage_directory_path.exists():
        Path.mkdir(storage_directory_path)
    return storage_directory_path


def set_data_dict(data_file):
    if os.path.getsize(data_file) == 0:
        return {}
    with open(data_file, "r") as f:
        return json.load(f)


def set_data_file(storage_path):
    data_file_path = storage_path.joinpath("data.json")
    if not data_file_path.exists():
        Path.touch(data_file_path)
    return data_file_path


def main():
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")
    data_file = set_data_file(set_data_directory())
    data_dict = set_data_dict(data_file)
    http_server = threading.Thread(target=run_http_server, daemon=True)
    socket_server = threading.Thread(
        target=run_socket_server,
        args=("0.0.0.0", 5000, data_dict, data_file),
        daemon=True,
    )
    try:
        socket_server.start()
        http_server.start()
        socket_server.join()
        http_server.join()
    except KeyboardInterrupt:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(b"STOP_SOCKET_SERVER", ("0.0.0.0", 5000))
            httpd.shutdown()
        logging.debug("Destroy all threads")
        logging.debug(f"socket alive? {socket_server.is_alive()}")
        logging.debug(f"http alive? {http_server.is_alive()}")


if __name__ == "__main__":
    main()
