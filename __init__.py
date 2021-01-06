import config
from component import mymysql

config.init()
mymysql.init(config.app_conf["mysql"])


def init():
    pass
