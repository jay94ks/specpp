"""std/net/{uri,ipendpoint,dns,tcp,httpclient}.md reference implementation."""
import socket
import http.client as _httplib
from urllib.parse import urlsplit


class Uri:
    def __init__(self, text):
        p = urlsplit(text)
        if not p.scheme or not p.netloc:
            raise ValueError("invalid uri: " + text)
        self._p = p
        self._text = text

    def scheme(self):
        return self._p.scheme

    def host(self):
        return self._p.hostname

    def port(self):
        if self._p.port:
            return self._p.port
        return 443 if self._p.scheme == "https" else 80

    def path(self):
        return self._p.path or "/"

    def query(self):
        return self._p.query or None

    def toString(self):
        return self._text


class IPAddress:
    def __init__(self, text):
        self._text = text

    def toString(self):
        return self._text


class IPEndPoint:
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def toString(self):
        return f"{self.address.toString()}:{self.port}"


class Dns:
    @staticmethod
    def resolve(hostname):
        infos = socket.getaddrinfo(hostname, None)
        seen = set()
        result = []
        for info in infos:
            ip = info[4][0]
            if ip not in seen:
                seen.add(ip)
                result.append(IPAddress(ip))
        if not result:
            raise ValueError("could not resolve " + hostname)
        return result


class TcpClient:
    def __init__(self):
        self._sock = None

    def connect(self, endpoint):
        self._sock = socket.create_connection((endpoint.address.toString(), endpoint.port))

    def send(self, data):
        self._sock.sendall(data)

    def receive(self, maxBytes):
        return self._sock.recv(maxBytes)

    def close(self):
        if self._sock:
            self._sock.close()

    def isConnected(self):
        return self._sock is not None


class TcpListener:
    def __init__(self, port):
        self._port = port
        self._sock = None

    def start(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", self._port))
        self._sock.listen(1)

    def acceptClient(self):
        conn, _ = self._sock.accept()
        client = TcpClient()
        client._sock = conn
        return client

    def stop(self):
        if self._sock:
            self._sock.close()


class HttpRequest:
    def __init__(self, method, uri):
        self.method = method
        self.uri = uri
        self.headers = {}
        self.body = None


class HttpResponse:
    def __init__(self, statusCode, headers, body):
        self.statusCode = statusCode
        self.headers = headers
        self.body = body


class HttpClient:
    def send(self, request):
        conn_cls = _httplib.HTTPSConnection if request.uri.scheme() == "https" else _httplib.HTTPConnection
        conn = conn_cls(request.uri.host(), request.uri.port())
        path = request.uri.path()
        if request.uri.query():
            path += "?" + request.uri.query()
        conn.request(request.method, path, body=request.body, headers=request.headers or {})
        resp = conn.getresponse()
        data = resp.read()
        conn.close()
        return HttpResponse(resp.status, dict(resp.getheaders()), data)

    def get(self, uri):
        return self.send(HttpRequest("GET", uri))

    def post(self, uri, body):
        req = HttpRequest("POST", uri)
        req.body = body
        return self.send(req)
