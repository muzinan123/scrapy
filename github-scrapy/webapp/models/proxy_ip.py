# -*- coding: utf-8 -*-
import logging
import datetime as dt
import urllib

from flask import url_for
import requests

from app import app, db

now = dt.datetime.now


class Proxy(db.Model):
    '''代理'''
    id = db.Column(db.Integer, primary_key=True)
    protocal = db.Column(db.String(20), nullable=False)
    ip = db.Column(db.String(39), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(300))
    anon = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    last_check = db.Column(db.DateTime)
    user = db.Column(db.String(30))
    passwd = db.Column(db.String(30))
    src = db.Column(db.String(30))

    gmt_created = db.Column(db.DateTime, default=now())
    db.Index('uk_ip_idx', ip, port, unique=True)

    def __init__(self, protocal, ip, port, **kwargs):
        self.protocal = protocal
        self.ip = ip
        self.port = port

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            logging.warning('Save GithubRecord Error, detail: %s.', str(e))
            db.session.rollback()

    @classmethod
    def get_by_pip(cls, protocal, ip, port):
        return cls.query.filter_by(protocal=protocal, ip=ip, port=port).first()

    def get_porxy(cls, **filter_by):
        return cls.query.filter_by(**filter_by).order_by(cls.id.desc())

    def to_json(self):
        json_dict = {
            'id': self.id,
            'ip': self.ip,
            'port': self.port,
            'protocal': self.protocal,
            'anon': self.anon or '',
            'location': self.location or '',
            'speed': self.speed or '',
            'last_check': str(self.last_check) or ''
        }
        return json_dict

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()

    @classmethod
    def get_pip(cls):
        return cls.query.order_by(cls.last_check.desc()).with_entities(
            cls.protocal, cls.ip, cls.port)

    @classmethod
    def verify(cls, ip, port):
        proxies = {
            'http': 'http://%s:%d' % (ip, port),
            'https': 'http://%s:%d' % (ip, port)
        }
        try:
            resp = requests.get(
                'https://www.baidu.com', proxies=proxies, timeout=3)
            return resp.status_code == requests.codes.ok
        except:
            pass
