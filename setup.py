import logging

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BlockingScheduler

from __init__ import init
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
    # scheduler.add_job(sync_polardb_slow_log.start, 'interval', minutes=1)
    # scheduler.add_job(sync_polardb_slow_log.start, 'interval', hours=24)
    print("server is started")
    scheduler.start()
