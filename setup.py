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


def test_one_day():
    sync_polardb_slow_log.start()


def run_one_day():
    hours = app_conf["trigger"]["hours"]
    for item in hours:
        scheduler.add_job(sync_polardb_slow_log.start, 'cron', hour=item)


if __name__ == '__main__':
    test_one_day()
    # run_one_day()
    print("server is started")
    scheduler.start()
