# -*- coding: utf-8 -*-
import os
import time
import datetime as dt
import logging
import urllib

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config
import requests

now = dt.datetime.now
today_alarmed = []

app = Flask(__name__)
db = SQLAlchemy(app)
# Flask-SQLAlchemy must be initialized before Flask-Marshmallow.
# ma = Marshmallow(app)
deploy_env = os.environ.get('DEPLOY_ENV', None)
if deploy_env == 'prd':
    app.config.from_object(config.ProductConfig)
elif deploy_env == 'pre':
    app.config.from_object(config.PreConfig)
elif deploy_env == 'test':
    app.config.from_object(config.TestingConfig)
else:
    app.config.from_object(config.DevelopConfig)


def send_to_titan(keyword, full_name):
    # 发送告警到titan
    param = urllib.urlencode({'full_name': full_name})
    link = '?'.join([app.config['GITHUB_RECORDS_URL'], param])
    msg = u'发现一个github代码仓库%s含有<em>%s</em>关键字，详情：%s' % (
        full_name, keyword, link
    )
    form_data = {
        'type': 'new_vulnerability',
        'data': {
            'job_name': u'GitHub代码检索',
            'vul_name': full_name,
            'creator': 'luxiao@zhongan.com',
            'level': 3,
            'type': 'app',
            'desc': msg
        }
    }
    r = requests.post(app.config['TITAN'], json=form_data)
    if r.status_code == 200:
        return r.json().get('success', None)


def send_mail(mails, title, msg):
    data = {
            "mails": mails,
            "msg": msg,
            "title": title,
            "channel": "aliyunDirectmail"
        }
    url = app.config['EMAIL_URL']
    res = requests.post(url, json=data)
    if res.status_code == 200:
        result = res.json()
        print result


def send_to_regulator(keyword, full_name):
    # 发送告警到故障台移动端
    param = urllib.urlencode({'full_name': full_name})
    link = '?'.join([app.config['GITHUB_RECORDS_URL'], param])
    msg = u'发现一个github代码仓库%s含有<em>%s</em>关键字，详情：%s' % (
        full_name, keyword, link
    )
    form_data = {
        'type': 'new',
        'data': {
            'mission_name': u'GitHub代码疑似泄漏:https://github.com%s' % full_name,
            'app_name': full_name,
            'user': 'sushuangfei@zhongan.io',
            'next_person': ['sushuangfei@zhongan.io', 'zhouchen@zhongan.io', 'david.jiang@zhongan.com'],
            'notify_person': [
                'wangmingbo@zhongan.com', 'xubin@zhongan.com',
                'luxiao@zhongan.io', 'liangliang@zhongan.io',
                'huma.hu@zhongan.com'],
            'level': 4,
            'type': 'security',
            'child_type': 'ILEI',
            'teams': ['PE'],
            'desc': msg
        }
    }
    mapi = '/mobile/api/mission'
    r = requests.post(app.config['REGULATOR'] + mapi, json=form_data)
    if r.status_code == 200:
        print '创建故障成功', r.content
        return r.json().get('success', None)
    else:
        print '创建故障失败', r.content
        send_mail('luxiao@zhongan.io', u'Github代码疑似泄漏发送故障台失败!',
                  str(r.status_code))


class GithubRecord(db.Model):
    '''github搜索结果'''
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(400),
                          db.ForeignKey('github_repo.full_name'))
    github_repo = db.relationship(
        'GithubRepo', backref=db.backref('repos', lazy='dynamic'))
    name = db.Column(db.String(200))
    avatar = db.Column(db.String(2000))
    keyword = db.Column(db.String(200))
    owner = db.Column(db.String(200))
    file_path = db.Column(db.String(1000))
    file_name = db.Column(db.String(500))
    lang = db.Column(db.String(20))
    snippet = db.Column(db.String(2000))
    indexed_at = db.Column(db.DateTime, nullable=False)
    gmt_created = db.Column(db.DateTime, nullable=False, default=now())
    db.Index(
        'uk_name_file_keyword_idx', full_name, file_path, keyword, unique=True)

    def __init__(self, full_name, github_repo, name, keyword, owner, file_path,
                 lang, snippet, indexed_at, avatar, file_name):
        self.full_name = full_name
        self.github_repo = github_repo
        self.name = name
        self.keyword = keyword
        self.owner = owner
        self.file_path = file_path
        self.file_name = file_name
        self.lang = lang
        self.snippet = snippet
        self.indexed_at = indexed_at
        self.avatar = avatar

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            logging.warning('Save GithubRecord Error, detail: %s.', str(e))
            db.session.rollback()

    @classmethod
    def get_by_uk(cls, full_name, file_path, keyword):
        return cls.query.filter_by(full_name=full_name, file_path=file_path,
                                   keyword=keyword).first()

    @classmethod
    def create(cls, full_name, name, keyword, owner, file_path, lang,
               snippet, indexed_at, avatar, file_name):
        repo = GithubRepo.get_by_full_name(full_name)
        if not repo:
            repo = GithubRepo(full_name, name, owner).save()
        if full_name not in today_alarmed and repo.enabled:
            today_alarmed.append(full_name)
            print today_alarmed
            # 发送titan告警
            print 'send to regulator', now()
            send_to_regulator(keyword, full_name)
        if repo.enabled:
            record = cls(full_name, repo, name, keyword, owner, file_path,
                         lang, snippet, indexed_at, avatar, file_name).save()
            return record

    @classmethod
    def get_records(cls, **filter_by):
        return cls.query.filter_by(**filter_by).order_by(cls.id.desc())

    @classmethod
    def get_by_page(cls, page, per_page=10, **filter_by):
        return cls.query.filter_by(**filter_by).paginate(page, per_page, False)

    def to_json(self):
        json_dict = {
            'id': self.id,
            'full_name': self.name,
            'keyword': self.keyword,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'lang': self.lang,
            'snippet': self.snippet,
            'indexed_at': self.indexed_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'avatar': self.avatar
        }
        return json_dict

    @classmethod
    def get_indexed_at_by_keyword(cls, keyword):
        if keyword in app.config['GITHUB_KEYWORDS']:
            last = cls.query.filter_by(keyword=keyword).order_by(
                cls.indexed_at.desc()).with_entities(cls.indexed_at).first()
            return last.indexed_at


class GithubRepo(db.Model):
    """github仓库"""
    full_name = db.Column(db.String(400), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    owner = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200))
    lang = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    enabled = db.Column(db.Boolean, default=True)
    gmt_created = db.Column(db.DateTime, nullable=False, default=now())

    def __init__(self, full_name, name, owner, description=None, lang=None):
        self.full_name = full_name
        self.name = name
        self.owner = owner
        self.description = description
        self.lang = lang

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            logging.warning('Save GithubRepo Error, detail: %s.', str(e))
            db.session.rollback()

    @classmethod
    def get_by_full_name(cls, full_name):
        return cls.query.filter_by(full_name=full_name).first()

    @classmethod
    def get_all_repos(cls):
        return cls.query.order_by(cls.gmt_created.desc())

    def to_json(self):
        format = '%Y-%m-%d %H:%M'
        json_dict = {
            'full_name': self.full_name,
            'owner': self.owner,
            'description': self.description,
            'lang': self.lang,
            'enabled': self.enabled,
            'gmt_created': self.gmt_created.strftime(format),
            '_links': self.links
        }
        return json_dict

    @property
    def links(self):
        if hasattr(self, '_links'):
            return self._links
        self._links = self.ops
        return self._links

    @property
    def ops(self):
        if hasattr(self, '_ops'):
            return self._ops
        all_ops = [
            {'rel': 'edit', 'method': 'put', 'label': u'编辑',
             'href': url_for('get_by_full_name', full_name=self.full_name)},
            {'rel': 'del', 'method': 'patch', 'label': u'删除',
             'href': url_for('get_by_full_name',
                             full_name=self.full_name, enabled=False)},
            {'rel': 'recover', 'method': 'patch', 'label': u'恢复',
             'href': url_for('get_by_full_name',
                             full_name=self.full_name, enabled=True)}
        ]
        ops = []
        if self.enabled:
            ops.append(all_ops[0])
            ops.append(all_ops[1])
        else:
            ops.append(all_ops[2])
        self._ops = ops
        return self._ops

    def update(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        return self.save()


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
    def http_verify(cls, ip, port):
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

    @classmethod
    def verify(cls, host, port, protocal, **kwargs):
        import socks
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

    @classmethod
    def clear(cls):
        while True:
            proxy_list = cls.query.order_by(cls.gmt_created.asc()).all()
            start = dt.datetime.now()
            for proxy in proxy_list:
                if not cls.verify(proxy.ip, proxy.port, proxy.protocal):
                    proxy.delete()
            sleep = 3600 - (dt.datetime.now() - start).total_seconds()
            if sleep > 0:
                print 'tr'
                time.sleep(sleep)


if __name__ == '__main__':
    # send_to_titan(u'众安保险', '/chendind/project006')
    # print GithubRecord.get_indexed_at_by_keyword('zhongan')
    # Proxy.clear()
    # send_to_regulator('test', 'only a test')
    send_mail('luxiao@zhongan.com', 'test', 'test')
