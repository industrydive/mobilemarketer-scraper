# https://github.com/aciobanu/docker-scrapy/blob/master/Dockerfile

FROM aciobanu/scrapy:latest
COPY requirements.txt /runtime/requirements.txt
RUN pip install -r /runtime/requirements.txt