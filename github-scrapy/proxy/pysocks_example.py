import socks


def verify_proxy(protocal, host, port, **kwargs):
    s = socks.socksocket()
    s.set_proxy(getattr(socks, protocal, socks.HTTP), host, port, **kwargs)
    s.settimeout(5)
    try:
        s.connect(("www.baidu.com", 80))
        get_req = """GET / HTTP/1.1\r\nHost: www.baidu.com\r\n\r\n"""
        s.send(get_req)
        return 'HTTP/1.1 200 OK' in s.recv(16)
    except Exception as e:
        print str(e)
    finally:
        s.close()


def verify_http():
    """
    > GET http://www.google.com HTTP/1.1
    > Host: www.google.com
    > ...

    < HTTP response
    """

    get_req = """GET http://www.ipip.net HTTP/1.1\r\n
Host: www.ipip.net\r\n\r\n"""
    host, port = '124.88.67.30', 80
    # host = '127.0.0.1' #proxy server IP
    # port = 8899              #proxy server port

    try:
        s = socks.socksocket()
        s.settimeout(5)
        s.connect((host, port))
        s.send(get_req)
        response = s.recv(8096)
        print response
        s.close()
    except Exception as e:
        print 'timeout'
        print str(e)
        s.close()


def get_proxy():
    s = socks.selfocksocket()
    s.set_proxy(socks.HTTP, "124.255.23.82", 80)
    return s


if __name__ == '__main__':
    verify_proxy('HTTP', '119.18.234.60', 80)
