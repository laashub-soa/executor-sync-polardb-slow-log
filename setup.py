import logging

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BlockingScheduler

from __init__ import init
from config import app_conf
from service import sync_polardb_slow_log

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
init()

scheduler = BlockingScheduler()
executors = {
    'default': ThreadPoolExecutor(20),
}
if __name__ == '__main__':
    sync_polardb_slow_log.start()
    # scheduler.add_job(sync_polardb_slow_log.start, 'cron', hour=app_conf["trigger"]["hour"])
    print("server is started")
    scheduler.start()
