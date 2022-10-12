#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        hostPort = ['127.0.0.1', 80]
        host = urllib.parse.urlparse(url).hostname
        port = urllib.parse.urlparse(url).port

        # if x exists then assign as x, else keep it as localhost:80
        hostPort[0] = host if host else hostPort[0]
        hostPort[1] = port if port else hostPort[1]
        
        return hostPort

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        res = data.split(" ")
        code = int(res[1])
        return code

    def get_headers(self,data):
        res = data.split("\r\n\r\n")
        header = res[0]
        return header

    def get_body(self, data):
        res = data.split("\r\n\r\n")
        body = res[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        hostPort = self.get_host_port(url)
        host = hostPort[0]
        port = hostPort[1]
        self.connect(host, port)

        path = urllib.parse.urlparse(url).path
        request = f"GET {path if path else '/'} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        self.sendall(request)
        res = self.recvall(self.socket)
        self.close()
        code = self.get_code(res)
        body = self.get_body(res)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        hostPort = self.get_host_port(url)
        host = hostPort[0]
        port = hostPort[1]
        self.connect(host, port)
        path = urllib.parse.urlparse(url).path
        params = urllib.parse.urlencode(args) if args else ""
        contentLength = len(params)

        request  = f"POST /{path} HTTP/1.1\r\nHost: {host}\r\nContent-type: application/x-www-form-urlencoded\r\nContent-length: {contentLength}\r\n\r\n{params}"
        # request += f"{params}"
        try:
            self.sendall(request)

            res = self.recvall(self.socket)
        except Exception as e:
            print(e)

        self.close()
        code = self.get_code(res)
        body = self.get_body(res)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
