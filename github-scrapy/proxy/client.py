#!/usr/bin/python
from __future__ import print_function
import socket
import sys


def get_http(host, port):
    """
    > GET http://www.google.com HTTP/1.1
    > Host: www.google.com
    > ...

    < HTTP response
    """

    get_req = """GET http://www.ipip.net HTTP/1.1\r\n
Host: www.ipip.net\r\n\r\n"""
    # host = '127.0.0.1' #proxy server IP
    # port = 8899              #proxy server port

    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((host, port))
        s.send(get_req)
        response = s.recv(8096)
        print(response)
        s.close()
    except socket.error as m:
        print(str(m))
        s.close()
        sys.exit(1)


def get_https(host, port):
    """
    > CONNECT www.google.com:443 HTTP/1.1
    > Host: www.google.com
    < .. read response to CONNECT request, must be 200 ...

    .. establish the TLS connection inside the tunnel

    > GET / HTTP/1.1
    > Host: www.google.com
    """
    conn_req = """CONNECT github.com:443 HTTP/1.1\r\nHost: github.com\r\n\r\n"""
    get_req = """GET / HTTP/1.1\r\nHost: github.com\r\n\r\n"""
    conn_req = """CONNECT baidu.com:443 HTTP/1.1\r\nHost: baidu.com\r\n\r\n"""
    get_req = """GET baidu.com/ HTTP/1.1\r\nHost: baidu.com\r\n\r\n"""

    #host = '127.0.0.1' #proxy server IP
    #port = 8899              #proxy server port

    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((host, port))
        s.send(conn_req)
        print(s.recv(8192))
        s.send(get_req)
        response = s.recv(8192)
        print(response)
        s.close()
    except socket.error as m:
        print(str(m))
        s.close()
        sys.exit(1)


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 1080
    get_http(ip, port)
    get_https(ip, port)
