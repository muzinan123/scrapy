# -*- coding: utf-8 -*-
# @Author blackrat  wangmingbo@zhongan.io
# @Time 2020-03-25 20:22
import os

ROOT_PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))


class BaseConfig(object):

    APP_NAME = 'git-dependency-track'
    APP_VERSION = '0.1'

    PROJECTS_DIR = os.path.join(ROOT_PATH, 'projects')

    DEPENDENCY_TRACK_HOST = 'http://127.0.0.1:8080'
    DEPENDENCY_TRACK_API_KEY = 'FQBl35HVhx1JggeQueaE141aOc2w4RNa'
    GITLAB_USER = 'secure'
    GITLAB_ENC_PASS = b'zaec_prd_3e1df09808088f36a1b782f03ac86a471fc394d4bb8032fa06479f7c27d1b50502'
    GITLAB_SERVER = 'https://git.zhonganinfo.com'


CONFIG_DICT = {
    'prd': BaseConfig,
    'pre': BaseConfig,
    'test': BaseConfig,
    'pretest': BaseConfig,
    'aliyun-common': BaseConfig
}

VPC_CONFIG_DICT = {
    'prd': BaseConfig,
    'test': BaseConfig,
    'aliyun-common': BaseConfig
}


def get_current_config():
    is_vpc = os.environ.get('IS_VPC', None)
    deploy_env = os.environ.get('DEPLOY_ENV', None)

    is_vpc = os.environ.get('IS_VPC', None)
    deploy_env = os.environ.get('DEPLOY_ENV', None)
    if is_vpc:
        return VPC_CONFIG_DICT.get(deploy_env, BaseConfig)
    return CONFIG_DICT.get(deploy_env, BaseConfig)


CURRENT_CONFIG = get_current_config()
