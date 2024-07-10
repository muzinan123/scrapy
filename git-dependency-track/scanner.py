# -*- coding: utf-8 -*-
# @Author blackrat  wangmingbo@zhongan.io
# @Time 2020-03-26 08:34
import os
import shutil
import subprocess
import requests
import json
import base64
from za_ec import za_dec
from urllib import parse
from git import Repo
from config import CURRENT_CONFIG


class GoScanRunningError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        s = 'GoScanRunningError, {0}'.format(self.msg)
        return s


class PythonScanRunningError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        s = 'PythonScanRunningError, {0}'.format(self.msg)
        return s


class NodjsScanRunningError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        s = 'NodjsScanRunningError, {0}'.format(self.msg)
        return s


class MavenRunningError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        s = 'MavenRunningError, {0}'.format(self.msg)
        return s


class UploadBomError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        s = 'UploadBomError, {0}'.format(self.msg)
        return s


class Scanner(object):

    def __init__(self):
        self._projects_dir = CURRENT_CONFIG.PROJECTaS_DIR
        self._api_key = CURRENT_CONFIG.DEPENDENCY_TRACK_API_KEY
        self._server_host = CURRENT_CONFIG.DEPENDENCY_TRACK_HOST
        self._user = CURRENT_CONFIG.GITLAB_USER
        self._pass = za_dec(CURRENT_CONFIG.GITLAB_ENC_PASS).decode('utf-8')

    def clone(self, repo_url, branch):
        repo_url_parse = parse.urlparse(repo_url)
        domain = repo_url_parse.netloc[repo_url_parse.netloc.rfind('@')+1:]
        # if there is no auth in url, add it
        if repo_url_parse.netloc.find('@') == -1:
            auth_domain = '{user}:{password}@{domain}'.format(user=self._user, password=self._pass, domain=domain)
            repo_url = repo_url.replace(domain, auth_domain)
        project_name = repo_url[repo_url.rfind('/') + 1:].replace('.git', '')
        if not os.path.exists(os.path.join(self._projects_dir, domain)):
            os.makedirs(os.path.join(self._projects_dir, domain))
        to_path = os.path.join(self._projects_dir, domain, project_name)
        if not os.path.exists(to_path):
            repo = Repo.clone_from(url=repo_url, to_path=to_path)
        else:
            repo = Repo(to_path)
        # pull the remote branch
        remote = repo.remote()
        remote.pull(branch)
        return (repo, to_path)

    def scan(self, repo_url, branch, group_name=''):
        '''
        :param repo_url:
        :param branch:
        :return:
        '''
        res = False
        repo_url_parse = parse.urlparse(repo_url)
        domain = repo_url_parse.netloc[repo_url_parse.netloc.rfind('@')+1:]
        p_name = repo_url[repo_url.rfind('/') + 1:].replace('.git', '')
        project_name = group_name + '/' + p_name
        repo, code_path = self.clone(repo_url, branch)

        # judge java project
        if os.path.exists(os.path.join(code_path, 'pom.xml')):
            res = self.scan_java(code_path, project_name, branch)
        elif os.path.exists(os.path.join(code_path, 'requirements.txt')):
            res = self.scan_python(code_path, project_name, branch)
        elif os.path.exists(os.path.join(code_path, 'package.json')):
            #print('Unkown project type, only support java , python')
            res = self.scan_nodejs(code_path, project_name, branch)
        elif os.path.exists(os.path.join(code_path, 'composer.json')):
            # return self.scan_php(code_path, project_name, branch)
            print('Unkown project type, only support java, python, nodejs, go')
        elif os.path.exists(os.path.join(code_path, 'go.mod')):
            res = self.scan_go(code_path, project_name, branch)
        else:
            print('Unkown project type, only support java , python, nodejs, go')
        shutil.rmtree(code_path) 
        return res
 
    def scan_python(self, code_path, project_name, branch):
        res = False
        try:
            cmd = ['cyclonedx-py -i requirements.txt -o bom.xml']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=code_path, shell=True)
            out, err = p.communicate()
            if p.returncode != 0:
                msg = err.decode()
                raise PythonScanRunningError(msg)
            else:
                bom_file_path = os.path.join(code_path, 'bom.xml')
                if os.path.exists(bom_file_path):
                    try:
                        self.submit_bom(project_name, branch, bom_file_path)
                        res = True
                    except UploadBomError as e:
                        print(e)
                else:
                    print('bom file not found')
                    raise UploadBomError('bom file not found')   
        except Exception as e:
            raise PythonScanRunningError(e)
        return res

    def scan_nodejs(self, code_path, project_name, branch):
        res = False
        try:
            npm_cmd = ['npm install --no-optional']
            npm_p = subprocess.Popen(npm_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=code_path, shell=True)
            out, err = npm_p.communicate()
            if npm_p.returncode != 0:
                print(err.decode()) 
            cmd = ['cyclonedx-bom -o bom.xml']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=code_path, shell=True)
            out, err = p.communicate()
            if p.returncode != 0:
                msg = err.decode()
                raise NodjsScanRunningError(msg)
            else:
                bom_file_path = os.path.join(code_path, 'bom.xml')
                if os.path.exists(bom_file_path):
                    try:
                        self.submit_bom(project_name, branch, bom_file_path)
                        res = True
                    except UploadBomError as e:
                        print(e)
                else:
                    print('bom file not found')
                    raise UploadBomError('bom file not found')
        except Exception as e:
            raise NodjsScanRunningError(e)
        return res

    def scan_go(self, code_path, project_name, branch):
        res = False
        try:
            cmd = ['cyclonedx-go -o bom.xml']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=code_path, shell=True)
            out, err = p.communicate()
            if p.returncode != 0:
                msg = err.decode()
                raise GoScanRunningError(msg)
            else:
                bom_file_path = os.path.join(code_path, 'bom.xml')
                if os.path.exists(bom_file_path):
                    try:
                        self.submit_bom(project_name, branch, bom_file_path)
                        res = True
                    except UploadBomError as e:
                        print(e)
                else:
                    print('bom file not found')
                    raise UploadBomError('bom file not found')
        except Exception as e:
            raise GoScanRunningError(e)
        return res

    def scan_java(self, code_path, project_name, branch):
        print('CODE_PATH:', code_path)
        res = False
        try:
            cmd = ['/var/local/apache-maven-3.6.3/bin/mvn clean cyclonedx:makeBom -DgroupId=org.cyclonedx -DartifactId=cyclonedx-maven-plugin -Dversion=1.6.5']
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=code_path, shell=True)
            out, err = p.communicate()
            print(out.decode(), err.decode())
            if p.returncode != 0:
                msg = str(cmd)
                raise MavenRunningError(msg)
            else:
                bom_file_path = os.path.join(code_path, 'target/bom.xml')
                if os.path.exists(bom_file_path):
                    try:
                        print('begin to submit bom...')
                        self.submit_bom(project_name, branch, bom_file_path)
                        res = True
                    except UploadBomError:
                        pass
                else:
                    print('bom file not found')
                    raise UploadBomError('bom file not found')
        except Exception as e:
            raise MavenRunningError(e)
        return res

    def submit_bom(self, project_name, branch, bom_path):
        headers = {
            'X-Api-Key': self._api_key,
            'Content-Type': 'application/json'
        }
        with open(bom_path, 'r') as bom_file:
            body_data = {
              "projectName": project_name,
              "projectVersion": branch,
              "autoCreate": True,
              "bom": base64.b64encode(bom_file.read().encode("utf-8")).decode("utf-8")
            }

            api_url = self._server_host + '/api/v1/bom'
            try:
                resp = requests.put(url=api_url, data=json.dumps(body_data), headers=headers)
                print(api_url, resp.status_code)
                if resp.status_code != 200:
                    print('upload failed:', resp.text)
                    raise UploadBomError('')
                else:
                    print('upload success..')
            except Exception as e:
                raise UploadBomError(e)
        print('finished submit bom..')


if __name__ == '__main__':
    scanner = Scanner()
    scanner.scan('https://za-wangmingbo:0w1InRy3(za)@git.zhonganinfo.com/zainfo/seraph-metadata.git', 'master')

