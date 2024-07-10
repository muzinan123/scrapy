#!/usr/bin/env python3
# encoding: utf-8
#

import gitlab
import os
import sys


class GitlabAPI(object):
    def __init__(self, *args, **kwargs):
        if os.path.exists('python-gitlab.cfg'):
            self.gl = gitlab.Gitlab.from_config('gitlab', ['python-gitlab.cfg'])
        elif os.path.exists(os.getenv('HOME') + '/.python-gitlab.cfg'):
            self.gl = gitlab.Gitlab.from_config('gitlab', [os.getenv('HOME') + '/.python-gitlab.cfg'])
        else:
            print('You need to make sure there is a file named "python-gitlab.cfg" or "~/.python-gitlab.cfg"')
            sys.exit(5)

    def get_user_id(self, username):
        user = self.gl.users.get_by_username(username)
        return user.id

    def get_group_id(self, groupname):
        group = self.gl.users.search(groupname)
        return group[0].id

    def get_all_projects(self):
        projects = self.gl.projects.list(all=True)
        result_list = []
        for project in projects:
            result_list.append(project.http_url_to_repo)
        return result_list

    def get_user_projects(self, userid):
        projects = self.gl.projects.owned(userid=userid, all=True)
        result_list = []
        for project in projects:
            result_list.append(project.http_url_to_repo)
        return result_list

    def get_group_projects(self, groupname):
        projects = self.gl.projects.owned(groupname=groupname, all=True)
        result_list = []
        for project in projects:
            result_list.append(project.http_url_to_repo)
        return result_list


if __name__ == '__main__':
    git = GitlabAPI()
    page = 1
    while True:
        proejcts = git.gl.projects.list(page=page)
        if proejcts:
            print(page)
            page += 1
