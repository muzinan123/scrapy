# -*- coding: utf-8 -*-
import os
import datetime as dt
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from webapp.config import *

now = dt.datetime.now

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


class GithubRecord(db.Model):
    '''github搜索结果'''
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(400),
                          db.ForeignKey('github_repo.full_name'))
    github_repo = db.relationship(
        'GithubRepo', backref=db.backref('repos', lazy='dynamic'))
    name = db.Column(db.String(200))
    keyword = db.Column(db.String(200))
    owner = db.Column(db.String(200))
    file_path = db.Column(db.String(1000))
    lang = db.Column(db.String(20))
    snippet = db.Column(db.String(2000))
    indexed_at = db.Column(db.DateTime, nullable=False)
    gmt_created = db.Column(db.DateTime, nullable=False, default=now())
    db.Index(
        'uk_name_file_keyword_idx', full_name, file_path, keyword, unique=True)

    def __init__(self, full_name, github_repo, name, keyword, owner, file_path,
                 lang, snippet, indexed_at):
        self.full_name = full_name
        self.github_repo = github_repo
        self.name = name
        self.keyword = keyword.decode('utf-8')
        self.owner = owner
        self.file_path = file_path.decode('utf-8')
        self.lang = lang
        self.snippet = snippet.decode('utf-8')
        self.indexed_at = indexed_at

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
               snippet, indexed_at):
        repo = GithubRepo.get_by_full_name(full_name)
        if not repo:
            repo = GithubRepo(full_name, name, owner).save()
        if repo.enabled:
            record = cls(full_name, repo, name, keyword, owner, file_path,
                         lang, snippet, indexed_at).save()
            return record

    @classmethod
    def get_records(cls, **filter_by):
        return cls.query.filter_by(**filter_by).order_by(cls.id.desc())

    def to_json(self):
        json_dict = {
            'id': self.id,
            'full_name': self.name,
            'keyword': self.keyword,
            'file_path': self.file_path,
            'lang': self.lang,
            'snippet': self.snippet,
            'indexed_at': self.indexed_at.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        return json_dict


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
