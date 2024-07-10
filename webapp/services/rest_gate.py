# -*- coding: utf-8 -*-
# author blackrat  wangmingbo@zhongan.com
# create date 16/5/30

import time
import hashlib
import uuid
from pymongo import MongoClient
from datetime import datetime
_CACHE = {}


class RestGate():

    def __init__(self, host, port, dbname):
        self._client = None
        self._db = None
        self._host = host
        self._port = port
        self._dbname = dbname
        self._time_out = 600
        self._duration = 300
        self.conn()

    def conn(self):
        if self._client is None:
            self._client = MongoClient(self._host, self._port)
        self._db = self._client[self._dbname]
        return self._db

    def add_auth(self, server_name, app_name, status, ip_list):
        db = self.conn()
        c_auth = db['auth']
        now = datetime.now()
        token = str(uuid.uuid1())

        try:
            c_auth.insert_one({"server_name": server_name,
                               "app_name": app_name,
                               "status": status,
                               "ip_list": ip_list,
                               "gmt_modify": now,
                               "gmt_create": now,
                               "token": token
                               })
        except Exception, e:
            print "add_auth exception :%s" % e

    def get_record(self, server_name, app_name):
        db = self.conn()
        c_auth = db.auth
        record = None
        key = hashlib.sha1(server_name + app_name).hexdigest()
        try:
            auth_record = c_auth.find_one({"server_name": server_name,
                                           "app_name": app_name, "status": 1})
            if auth_record:
                record = {"token": auth_record[
                    "token"], "ip_list": auth_record["ip_list"]}
        except Exception, e:
            print "get_record exception : %s " % e
        # 将结果,更新/添加在内存中
        _CACHE[key] = {"value": record, "time": time.time()}
        return record

    def is_obsolete(self, cache_entry, duration):
        ''' 检查cache有没有过期  过期则删除cache '''
        if time.time() - cache_entry['time'] > duration:
            del cache_entry
            return True
        return False

    def get_cache_record(self, server_name, app_name):
        key = hashlib.sha1(server_name + app_name).hexdigest()
        if _CACHE.has_key(key) and not self.is_obsolete(_CACHE[key], self._duration):
            record = _CACHE[key]["value"]
            if not record:
                record = self.get_record(server_name, app_name)
        else:
            record = self.get_record(server_name, app_name)
        return record

    def auth(self, server_name, app_name, client_ip, timestamp, hash):
        """

        :param server_name:  服务端 服务名 string
        :param app_name:  应用名
        :param client_ip:  客户端IP
        :param timestamp:  客户端提供的时间戳
        :param hash:  客户端提供的Hash
        :return: True|False  认证成功或失败
        """
        res = False
        record = self.get_cache_record(server_name, app_name)
        if record:
            now_ts = time.time()
            # 如果timestamp超时且没有获取到token
            if abs(now_ts - timestamp) < self._time_out and (client_ip in record["ip_list"] or "*" in record["ip_list"]):
                verify_hash = hashlib.sha1(
                    app_name + str(timestamp) + record["token"]).hexdigest()
                if verify_hash == hash:
                    res = True
        return res

if __name__ == "__main__":
    _HOST = "10.253.100.61"
    _PORT = 27017
    _DB = "rest_gate"
    restgate = RestGate(_HOST, _PORT, _DB)
    # restgate.add_auth("test_server","app1",1,["192.168.1.2"])
    ts = time.time()
    print int(ts)
    server_name = 'blacklist'
    app_name = 'securityAnalyzeCenter'
    record = restgate.get_cache_record(server_name, app_name)
    hash_str = hashlib.sha1(app_name + str(ts) + record["token"]).hexdigest()
    print hash_str
    print restgate.auth(server_name, app_name, "10.139.176.30", ts, hash_str)
