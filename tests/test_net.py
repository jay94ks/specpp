import http.server
import threading
import unittest

from spp_std.net_ import Uri, IPAddress, IPEndPoint, Dns, TcpClient, TcpListener, HttpClient


class UriTest(unittest.TestCase):
    def test_components(self):
        u = Uri("https://example.com:8443/a/b?x=1")
        self.assertEqual(u.host(), "example.com")
        self.assertEqual(u.scheme(), "https")
        self.assertEqual(u.port(), 8443)
        self.assertEqual(u.path(), "/a/b")
        self.assertEqual(u.query(), "x=1")


class IPEndPointTest(unittest.TestCase):
    def test_to_string(self):
        ep = IPEndPoint(IPAddress("127.0.0.1"), 8080)
        self.assertEqual(ep.toString(), "127.0.0.1:8080")


class DnsTest(unittest.TestCase):
    def test_resolve_localhost(self):
        addrs = Dns.resolve("localhost")
        self.assertTrue(len(addrs) >= 1)


class TcpTest(unittest.TestCase):
    def test_send_and_receive_over_loopback(self):
        listener = TcpListener(0)
        # port 0 은 OS가 빈 포트를 골라주므로, 실제로 바인딩된 포트를 알아내기 위해
        # 소켓을 직접 살짝 들여다본다 (테스트 편의를 위한 예외적 접근).
        listener._sock = None
        import socket
        listener._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener._sock.bind(("127.0.0.1", 0))
        listener._sock.listen(1)
        port = listener._sock.getsockname()[1]

        received = {}

        def server():
            client = listener.acceptClient()
            received["data"] = client.receive(1024)
            client.close()

        server_thread = threading.Thread(target=server)
        server_thread.start()

        client = TcpClient()
        client.connect(IPEndPoint(IPAddress("127.0.0.1"), port))
        client.send(b"hello")
        client.close()

        server_thread.join()
        listener.stop()

        self.assertEqual(received["data"], b"hello")


class _EchoHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        pass


class HttpClientTest(unittest.TestCase):
    def test_get_against_local_server(self):
        server = http.server.HTTPServer(("127.0.0.1", 0), _EchoHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        try:
            resp = HttpClient().get(Uri(f"http://127.0.0.1:{port}/"))
            self.assertEqual(resp.statusCode, 200)
            self.assertEqual(resp.body, b"ok")
        finally:
            server.shutdown()
            thread.join()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
