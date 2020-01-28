from multiprocessing import Process
import time
from datetime import datetime, timedelta
import inspect

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler 

from stocklab.agent.ebest import EBest
from stocklab.agent.data import Data
from stocklab.db_handler.mongodb_handler import MongoDBHandler

ebest_ace = EBest("ACE")
ebest_ace.login()
mongo = MongoDBHandler()

def run_process_trading_scenario(code_list, date):
    p = Process(target=run_trading_scenario, args=(code_list, date))
    p.start()
    p.join()
    print("run porcess join")

def run_trading_scenario(code_list, date):
    tick = 0
    print(code_list, date, tick)

    while tick < 20:
        print("ticK:", tick)
        for code in code_list:
            current_price = ebest_ace.get_price_n_min_by_code(date, code, tick)
            print("current price", current_price)
            time.sleep(1)
            buy_order_list = ebest_ace.order_stock(code, "2", current_price["시가"], "2", "00")
            buy_order = buy_order_list[0]
            buy_order["amount"] = 2
            mongo.insert_item(buy_order, "stocklab_test", "order")
            sell_order_list = ebest_ace.order_stock(code, "1", current_price["종가"], "1", "00")
            sell_order = sell_order_list[0]
            sell_order["amount"] = 1
            mongo.insert_item(sell_order, "stocklab_test", "order")
        tick += 1    

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    codes = ["180640", "005930"]
    day = datetime.now() - timedelta(days=4)
    day = day.strftime("%Y%m%d")
    print(day)
    scheduler.add_job(func=run_process_trading_scenario, trigger="date", run_date=datetime.now(), id="test", 
                    kwargs={"code_list":codes, "date":day})
    scheduler.start()
    """
    while True:
        print("waiting...", datetime.now())
        time.sleep(1)
    """