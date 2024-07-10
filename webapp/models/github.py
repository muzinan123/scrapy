# -*- coding: utf-8 -*-
import logging
import datetime as dt
import urllib

from flask import url_for
import requests

from app import app, db

now = dt.datetime.now


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


class GithubRecord(db.Model):
    '''github搜索结果'''
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(400),
                          db.ForeignKey('github_repo.full_name'))
    github_repo = db.relationship(
        'GithubRepo', backref=db.backref(
            'repos', lazy='dynamic', cascade="all, delete-orphan"))
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
            # 发送titan告警
            print str(now()), 'send to titan'
            send_to_titan(keyword, full_name)
        if repo.enabled:
            record = cls(full_name, repo, name, keyword, owner, file_path,
                         lang, snippet, indexed_at, avatar, file_name).save()
            return record

    @classmethod
    def get_records(cls, **filter_by):
        return cls.query.filter_by(**filter_by).order_by(cls.id.desc())

    @classmethod
    def get_by_page(cls, page, per_page=10, **filter_by):
        return cls.query.filter_by(**filter_by).join(GithubRepo).filter_by(
            enabled=True).order_by(cls.id.desc()).paginate(page, per_page, False)

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
    def get_all_repos(cls, **filter_by):
        return cls.query.filter_by(
            **filter_by).order_by(cls.enabled.desc())

    def to_json(self):
        format = '%Y-%m-%d %H:%M'
        json_dict = {
            'full_name': self.full_name,
            'owner': self.owner,
            'description': self.description or '',
            'lang': self.lang or '',
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
            {'rel': 'github', 'method': 'get', 'label': u'前往GitHub',
             'href': 'https://github.com%s' % self.full_name},
            {'rel': 'disable', 'method': 'patch', 'label': u'加入白名单',
             'href': url_for('get_by_full_name', owner=self.owner,
                             name=self.name, enabled=False)},
            {'rel': 'recover', 'method': 'patch', 'label': u'恢复',
             'href': url_for('get_by_full_name', owner=self.owner,
                             name=self.name, enabled=True)},
            {'rel': 'delete', 'method': 'delete', 'label': u'删除',
             'href': url_for('get_by_full_name', owner=self.owner,
                             name=self.name)}
        ]
        ops = [all_ops[0], all_ops[3]]
        if self.enabled:
            ops.append(all_ops[1])
        else:
            ops.append(all_ops[2])
        self._ops = ops
        return self._ops

    def update(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        return self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

if __name__ == '__main__':
    # send_to_titan(u'众安保险', '/chendind/project006')
    print GithubRecord.get_indexed_at_by_keyword('zhongan')
