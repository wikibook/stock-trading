import time
from datetime import datetime

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler 

from stocklab.agent.ebest import EBest
from stocklab.agent.data import Data
from stocklab.db_handler.mongodb_handler import MongoDBHandler

def collect_code_list():
    ebest = EBest("DEMO")
    mongodb = MongoDBHandler()
    ebest.login()
    result = ebest.get_code_list("ALL")
    mongodb.delete_items({}, "stocklab", "code_info")
    mongodb.insert_items(result, "stocklab", "code_info")
    print("finished")

def collect_stock_info():
    ebest = EBest("DEMO")
    mongodb = MongoDBHandler()
    ebest.login()
    mongodb.delete_items({}, "stocklab", "price_info")
    mongodb.delete_items({}, "stocklab", "credit_info")
    mongodb.delete_items({}, "stocklab", "short_info")
    mongodb.delete_items({}, "stocklab", "agent_info")
    code_list = mongodb.find_items({}, "stocklab", "code_info")
    target_code = set([item["단축코드"] for item in code_list])
    today = datetime.today().strftime("%Y%m%d")
    print(today)
    collect_list = mongodb.find_items({"날짜":today}, "stocklab", "price_info").distinct("code")
    for col in collect_list:
        target_code.remove(col)

    for code in target_code:
        print(code)
        time.sleep(1)
        result_price = ebest.get_stock_price_by_code(code, "500")
        if len(result_price) > 0:
            print(result_price)
            mongodb.insert_items(result_price, "stocklab", "price_info")

        result_credit = ebest.get_credit_trend_by_code(code, today)
        if len(result_credit) > 0:
            print(result_credit)
            mongodb.insert_items(result_credit, "stocklab", "credit_info")

        result_short = ebest.get_short_trend_by_code(code, sdate="20180101", edate=today)
        if len(result_short) > 0:
            print(result_short)
            mongodb.insert_items(result_short, "stocklab", "short_info")

        result_agent = ebest.get_agent_trend_by_code(code, fromdt="20180101", todt=today)
        if len(result_agent) > 0:
            print(result_agent)
            mongodb.insert_items(result_agent, "stocklab", "agent_info")
    
if __name__ == '__main__':
    collect_code_list()
    collect_stock_info()