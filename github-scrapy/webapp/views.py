# -*- coding: utf-8 -*-
import logging
import datetime as dt

from webargs import fields
from webargs.flaskparser import use_args, parser
from flask import (jsonify, render_template, request, session)

from app import app
from models import GithubRecord, GithubRepo
from services import sso


@app.route('/health')
def health():
    return 'Healthy, World!'


@app.route('/')
@sso.require_login
def index(user):
    return render_template('starter.html', user=user)


@app.route('/logout')
def logout():
    user = session.pop('user', None)
    if user:
        logging.info('User:%s logout.' % user['username'])
    return sso.logout()


@app.route('/api/v1/github_repo/<owner>/<name>', methods=['GET', 'PATCH', 'DELETE'])
@sso.require_admin
def get_by_full_name(owner, name, user):
    full_name = '/%s/%s' % (owner, name)
    repo = GithubRepo.get_by_full_name(full_name)
    if not repo:
        return jsonify({'code': 404, 'msg': 'Not found.'})
    if request.method == 'GET':
        return jsonify({'code': 200, 'data': repo.to_json()})
    elif request.method == 'PATCH':
        enabled_args = {'enabled': fields.Boolean(required=True)}
        args = parser.parse(enabled_args)
        logging.info(u'用户:%s修改github仓库%s状态为%d' % (
            user['name'], full_name, args['enabled']))
        result = repo.update(enabled=args['enabled'])

    elif request.method == 'DELETE':
        result = repo.delete()
    if result:
        return jsonify({'code': 200, 'msg': u'操作成功'})
    else:
        return jsonify({'code': 500, 'msg': u'操作异常'})



@app.route('/view/github_records', methods=['GET'])
@sso.require_login
def view_github_records(user):
    if request.method == 'GET':
        pagination_args = {
            'page': fields.Int(missing=1),
            'full_name': fields.Str(),
            'keyword': fields.Str()
        }
        args = parser.parse(pagination_args)
        page = args.pop('page')
        paginate = GithubRecord.get_by_page(page, **args)
        return render_template(
            'github_records.html', user=user, pagination=paginate,
            keywords=app.config['GITHUB_KEYWORDS'])


@app.route('/view/github_repos', methods=['GET'])
@sso.require_login
def view_github_repos(user):
    if request.method == 'GET':
        view_args = {
            'enabled': fields.Boolean(),
            'owner': fields.Str(),
            'name': fields.Str()}
        args = parser.parse(view_args)
        repos = GithubRepo.get_all_repos(**args)
        data = [repo.to_json() for repo in repos]
        return render_template('github_repos.html', user=user, repos=data)
