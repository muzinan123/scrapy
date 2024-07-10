# -*- coding: utf-8 -*-

import json
from urllib import urlencode
from urllib2 import urlopen
from functools import wraps
from urlparse import urlparse, urlunparse, parse_qs
from flask import render_template, redirect, request, session, abort

from app import app

admin_users = ['luxiao@zhongan.com', 'wangmingbo@zhongan.com',
               'bin.xu@zhongan.com']


def logout():
    return redirect(app.config['SSO_LOGOUT'])


def redirect_to_sso():
    return redirect('{}?{}'.format(
        app.config['SSO_LOGIN'],
        urlencode(
            {'service': app.config['SSO_SERVICE'], 'target': request.url})
    ))


def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'ticket' in request.args:
            valid = validate_service(request.args['ticket'])
            if valid:
                o = urlparse(request.url)
                query = parse_qs(o.query)
                query.pop('ticket')
                o = o._replace(query=urlencode(query, True))
                return redirect(o.geturl())
            else:
                return redirect('/')
        if 'user' not in session:
            return redirect_to_sso()
        kwargs['user'] = session['user']
        return f(*args, **kwargs)

    return decorated_function


def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user', {}).get('email', None) in admin_users:
            kwargs['user'] = session['user']
            return f(*args, **kwargs)
        else:
            abort(403)
    return decorated_function


def validate_service(ticket):
    query = dict()
    query['service'] = app.config['SSO_SERVICE']
    query['ticket'] = ticket
    url = '{}?{}'.format(
        app.config['SSO_VALIDATE'],
        urlencode(query),
    )
    res = urlopen(url).read()
    user = json.loads(res)
    if user.get('username'):
        session['user'] = user
        return True
    else:
        return False

'''
@app.before_request
def before_request():
    # 开发环境自动加上匿名用户，跳过sso
    if 'user' not in session and app.config.get('DEBUG', None):
        user = {
            'username': 'anonymous',
            'email': 'anonymous@zhongan.com',
            'name': u'未登录用户',
            'no:': '-1',
            'role': 'guest'
        }
        session['user'] = user
'''
