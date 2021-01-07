# 后端
FROM python:3.7
WORKDIR /usr/src/app
RUN rm -rf *
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
RUN python3 -m compileall -b .
RUN find . -name "*.py" |xargs rm -rf
# 声明
MAINTAINER tristan "https://github.com/laashub-soa/executor-sync-polardb-slow-log"
VOLUME /usr/src/app/configs
CMD [ "python", "./setup.pyc" ]