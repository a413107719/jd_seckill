# -*- coding:utf-8 -*-
import time
import requests
import json
import random

from datetime import datetime
from datetime import timedelta
from jd_logger import logger
from config import global_config


class Timer(object):
    def __init__(self, sleep_interval=0.5):
        # '2018-09-28 22:45:50.000'
        self.timeNow = datetime.today()
        self.oldTime = datetime.strptime(global_config.getRaw('config','buy_time'), "%Y-%m-%d %H:%M:%S.%f")
        self.setTime = datetime.strptime(datetime.strftime(self.timeNow,"%Y-%m-%d") + " 09:59:58.500", "%Y-%m-%d %H:%M:%S.%f") if self.oldTime<=self.timeNow else self.oldTime
        self.buy_time = self.setTime - timedelta(seconds=random.randint(1, 3),milliseconds=random.randint(100,300))
        self.buy_time_ms = int(time.mktime(self.buy_time.timetuple()) * 1000.0 + self.buy_time.microsecond / 1000)
        self.sleep_interval = sleep_interval
        self.diff_time = self.local_jd_time_diff()
        self.kill_time = timedelta(seconds=(150 + random.randint(10,30)),milliseconds=random.randint(100,1000))

    def jd_time(self):
        """
        从京东服务器获取时间毫秒
        :return:
        """
        url = 'https://a.jd.com//ajax/queryServerData.html'
        ret = requests.get(url).text
        js = json.loads(ret)
        return int(js["serverTime"])

    def local_time(self):
        """
        获取本地毫秒时间
        :return:
        """
        return int(round(time.time() * 1000))

    def time_now(self):
        return datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S.%f")

    def local_jd_time_diff(self):
        """
        计算本地与京东服务器时间差
        :return:
        """
        return self.local_time() - self.jd_time()

    def kill_not_out_time(self):
        return datetime.now() <= self.buy_time + self.kill_time

    def start(self):
        logger.info('正在等待到达设定时间:{}，检测本地时间与京东服务器时间误差为【{}】毫秒'.format(self.buy_time, self.diff_time))
        while True:
            # 本地时间减去与京东的时间差，能够将时间误差提升到0.1秒附近
            # 具体精度依赖获取京东服务器时间的网络时间损耗
            if self.local_time() - self.diff_time >= self.buy_time_ms:
                logger.info('时间到达，开始执行……')
                break
            else:
                time.sleep(self.sleep_interval)

if __name__ == "__main__":
    testTimer = Timer()