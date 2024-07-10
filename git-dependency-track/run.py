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
    page = 0
    while True:
        try:
            projects = group.projects.list(page=page)
            if projects:
                print('begin scan group %s, page: %s', group_name, page)
                page += 1
                for p in projects:
                    print(p.http_url_to_repo)
                    try:                                
                        scanner.scan(p.http_url_to_repo, 'master', group_name) 
                    except Exception as e:
                        print('scan failed: ', e)
            else:
                print('finished scan..., page:', page, ' group_name:', group_name)
                break 
        except Exception as e:
            print('get projects of page: ', page, ' failed...', 'Error:', e)
            break 


def scan_from_list(project_list_file):
    scanner = Scanner()
    with open(project_list_file, 'r') as list_file:
        for line in list_file:
            print('scan ', line)
            scanner.scan(line.strip(), 'master')


import sys
repo_url = eval(sys.argv[1])
branch = eval(sys.argv[2])


def scan_from_project(repo_url, branch):
    try:
        scanner = Scanner()
        scanner.scan(repo_url, branch)
    except Exception as e:
        print('scan failed: ', e)

        
if __name__ == '__main__':
    #scan_from_gitlab('za')
    #scan_from_list('projects.txt')
    scan_from_project(repo_url, branch)