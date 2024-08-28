# Scheme/protocol            Path
# httpScheme://example.org/index.html
#               Hostname


import socket
import ssl


class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        # assert self.sche/me == "http", "Only 'http' scheme is supported"  - for only http
        assert self.scheme in ["http","https"]
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        if ":" in self.host:
            self.host, port = self.host.split(":",1)
            self.port = int(port)

    # Method to download the web page at the given URL
    def request(self):
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, self.port))
        # wrapping the socket with the ssl lib for https
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s,server_hostname=self.host)

        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"  # End of request headers
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        # Read the content (body) of the response
        content = response.read()
        s.close()
        return content

    # Method to display the response body in a readable form (without HTML tags)
    def show(self, body):
        in_tag = False
        for c in body:
            if c == "<" and " {":
                in_tag = True
            elif c == ">" and "} ":
                in_tag = False
            elif not in_tag:
                print(c, end="")

    # Method to load a webpage by stringing request and show together
    def load(self):
        body = self.request()
        self.show(body)


# The following code runs the load method from the command line
if __name__ == "__main__":
    import sys

    url = URL(sys.argv[1])
    url.load()


#     run on cmd -- python Oceanbrowser.py https://browser.engineering/examples/example1-simple.html
