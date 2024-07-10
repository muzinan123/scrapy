# -*- coding: utf-8 -*-
class Config(object):
    # flask
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'r/\x04.\xd3j\x0ez\xb5\xa3D\xf48\x12\xe1\xac'

    GITHUB_KEYWORDS = [u'众安保险', 'zhongan', u'众安在线']

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///github.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # sso
    SSO_SERVER_URL = 'http://nsso.zhonganonline.com'
    SSO_LOGIN = SSO_SERVER_URL + '/login/'
    SSO_VALIDATE = SSO_SERVER_URL + '/validate/'
    SSO_LOGOUT = SSO_SERVER_URL + '/logout/'
    SSO_SERVICE = 'github'
    SSO_SECRET_KEY = 'fcad92e30356482f'
    SSO_ROLE_URL = 'http://auth-test.zhonganonline.com/auth/api/role'

    # titan
    TITAN = 'http://titan.zhonganonline.com/api/mission'

    # github_records
    GITHUB_RECORDS_URL = 'http://gitmonitor.zhonganonline.com/view/github_records'

    # regulator
    # REGULATOR = 'http://10.253.11.237:8803'
    REGULATOR = 'http://regulator.zhonganonline.com'

    EMAIL_URL = "http://10.139.113.22:8082/alarm/sendEmail"


class ProductConfig(Config):
    SSO_ROLE_URL = 'http://auth.zhonganonline.com/auth/api/role'
    pass


class PreConfig(Config):
    SSO_ROLE_URL = 'http://auth-uat.zhonganonline.com/auth/api/role'
    pass


class DevelopConfig(Config):
    # SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1:3306/blacklist'
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
