#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()\
        # parse request and handle request
        try:
            self.parse_request(self.data.decode("utf-8"))
        except:
            self.handle_404()
        

    def parse_request(self, request):
        # parse request to get method and path
        request = request.split("\r\n")
        request_line = request[0].split(" ")
        method = request_line[0]
        path = request_line[1]
        # check if method is GET
        if method == "GET":
            path = "www" + path 
            #check that path does not try to access parent directory
            if "../" in path:
                sec = self.security_check(path)
                if not sec:
                    self.handle_404()
                    return
                
            # check if path is valid
            if path.endswith("/") or path.endswith(".html") or path.endswith(".css"):
                self.serve_file(path)
            else:
                self.handle_301(path)
        else:
            self.handle_405()
    
    def security_check(self, path):
        # iterate through path to check if it goes beyond www
        path = path.split("/")
        point = 0
        for i in range(len(path)):
            if path[i] == "..":
                point -=1
            else:
                point +=1
            if point < 0:
                return False
        return True

    def serve_file(self, path):
        # check if path exists
        if path.endswith("/"):
            path += "index.html"
        try:
            file = open(path, "r")
            if path.endswith(".html"):
                self.handle_200(file.read(), mime_type="text/html")
            elif path.endswith(".css"):
                self.handle_200(file.read(), mime_type="text/css")
        except:
            self.handle_404()

    def handle_200(self, content, mime_type="text/html"):
        # handle 200 OK
        self.request.sendall(bytearray("HTTP/1.1 200 OK\r\n", 'utf-8'))
        self.request.sendall(bytearray("Content-Type: " + mime_type + "\r\n", 'utf-8'))
        self.request.sendall(bytearray("\r\n", 'utf-8'))
        self.request.sendall(bytearray(content, 'utf-8'))

    def handle_301(self, path):
        # handle 301 Moved Permanently
        self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\n", 'utf-8'))
        self.request.sendall(bytearray("Location: " + path[3:] + "/\r\n", 'utf-8'))
        self.request.sendall(bytearray("\r\n", 'utf-8'))

    def handle_404(self):
        # handle 404 Not Found
        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n", 'utf-8'))
        self.request.sendall(bytearray("Connection: close\r\n", 'utf-8'))
        self.request.sendall(bytearray("\r\n", 'utf-8'))
        # send 404 html message
        self.request.sendall(bytearray("<!DOCTYPE html>\n<html>\n<title>404 Page not found</title>\n<body>\n<h1>404 Not Found</h1>\n</body>\n</html>", 'utf-8'))


    def handle_405(self):
        # handle 405 Method Not Allowed
        self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n", 'utf-8'))
        self.request.sendall(bytearray("Connection: close\r\n", 'utf-8'))
        self.request.sendall(bytearray("\r\n", 'utf-8'))
        # send 405 html message
        self.request.sendall(bytearray("<!DOCTYPE html>\n<html>\n<title>405 Method Not Allowed</title>\n<body>\n<h1>405 Method Not Allowed</h1>\n</body>\n</html>", 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
