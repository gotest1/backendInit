import http.client
import json
import time
import requests
from _thread import start_new_thread, allocate_lock
import pandas as pd
from io import StringIO

timers = {}
lock = allocate_lock()
 
#all poll times are in minutes since that is the minimum granularity

def invokeCallbacks(pollTime, symbol, pd):
    for func in timers[pollTime][symbol]:
        func(pd)

def performQueryAndFillData(pollTime, symbol, sleepBeforeQuery):
    time.sleep(sleepBeforeQuery)
    url = "https://www.alphavantage.co/query"
    function = "TIME_SERIES_INTRADAY"
    data = { "function": function,
            "outputsize": "compact",
             "symbol": symbol,
             "interval": str(pollTime) + "min",
             "datatype": "csv",
             "apikey": "60MM3J3ZP4VBFHJK" }
    page = requests.get(url, params = data)
    if page.status_code != 200:
        performQueryAndFillData(pollTime, symbol, 0)
        return
    invokeCallbacks(pollTime, symbol, pd.read_csv(StringIO(page.content.decode())))

def fillStocksData(pollTime):
    query_strs = []
    lock.acquire()
    sleep_offset = 0
    for stock in timers[pollTime].keys():
        start_new_thread(performQueryAndFillData, (pollTime, stock, sleep_offset,))
        sleep_offset += 2
    lock.release()

def timerPollerThread(pollTime):
    while (1):
        if pollTime not in timers:
            return
        fillStocksData(pollTime)
        time.sleep(pollTime * 60)

def registerPoller(pollTime, stockName, callbackFunction):
    startThread = False
    lock.acquire()
    if pollTime not in timers:
        timers[pollTime] = {}
        startThread = True
    if (stockName not in timers[pollTime]):
        timers[pollTime][stockName] = set([callbackFunction])
    else:
        timers[pollTime][stockName].add(callbackFunction)
    lock.release()
    if startThread:
        start_new_thread(timerPollerThread, (pollTime,))

def unregisterPoller(pollTime, stockName, callbackFunction):
    if pollTime not in timers:
        return
    if stockName == "":
        lock.acquire()
        timers.pop(pollTime)
        lock.release()
        return
    lock.acquire()
    if (stockName in timers[pollTime]):
        if (callbackFunction in timers[pollTime][stockName]):
            timers[pollTime][stockName].remove(callbackFunction)
            if (len(timers[pollTime][stockName]) == 0):
                timers[pollTime].pop(stockName)
        if (len(timers[pollTime].keys()) == 0):
            timers.pop(pollTime)
    lock.release()
