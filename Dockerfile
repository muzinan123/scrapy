FROM dev-registry.zhonganonline.com:5000/env/python:2.7-alpine
MAINTAINER Lu Xiao <luxiao@zhongan.com>
COPY . /blacklist
WORKDIR /blacklist

# RUN apk add --no-cache --virtual .build-deps ca-certificates \
#     && update-ca-certificates

RUN pip install -r requirements.txt -i http://pypi.zhonganonline.com/xiaoyunlong/pypi/+simple --trusted-host pypi.zhonganonline.com --timeout 120 --retries 2

#RUN python manage.py db upgrade

ENTRYPOINT ["/usr/local/bin/gunicorn", "--config=/blacklist/ops/deploy/gunicorn_cfg.py"]
CMD ["app:app"]

EXPOSE 8080
