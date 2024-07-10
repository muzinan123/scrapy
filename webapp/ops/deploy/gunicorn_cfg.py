bind = "0.0.0.0:8080"
chdir = "/alidata1/admin/apps/github/github/webapp"
loglevel = "INFO"
workers = "4"
worker_class = "sync"
reload = True
raw_env = [
   'DEPLOY_ENV=prd',
]

errorlog = "/alidata1/admin/apps/github/github/webapp/logs/g_error.log"
accesslog = "/alidata1/admin/apps/github/github/webapp/logs/g_access.log"
