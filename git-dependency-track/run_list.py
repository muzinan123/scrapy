# -*- coding: utf-8 -*-
# @Author blackrat  wangmingbo@zhongan.io
# @Time 2020-03-25 15:46

from scanner import Scanner
from py_gitlab import GitlabAPI 


def scan_from_gitlab(group_name):
    zagit = GitlabAPI()
    scanner = Scanner()
    group = zagit.gl.groups.get(group_name, lazy=True)
    if not group:
        print('group_name not found: ', group_name)
        return
    page = 1
    while True:
        try:
            projects = group.projects.list(page=page)
            if projects:
                page += 1
                for p in projects:
                    print(p.http_url_to_repo)
                    scanner.scan(p.http_url_to_repo, 'master') 
        except Exception as e:
            print('get projects of page: ', page, ' failed...', 'Error:', e)
            break 


def scan_from_list(project_list_file):
    scanner = Scanner()
    with open(project_list_file, 'r') as list_file:
        for line in list_file:
            print('scan ', line)
            scanner.scan(line.strip(), 'master')


if __name__ == '__main__':
    scan_from_list('projects.txt')
