import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler 
from stocklab.agent.ebest import EBest
from stocklab.db_handler.mongodb_handler import MongoDBHandler
from multiprocessing import Process

ebest_demo = EBest("DEMO")
ebest_demo.login()
mongo = MongoDBHandler()

def run_process_trading_scenario(code_list):
    p = Process(target=trading_scenario, args=(code_list,))
    p.start()
    p.join()
    print("run process join")

def check_buy_completed_order(code):
    """매수완료된 주문은 매도 주문
    """
    buy_completed_order_list = list(mongo.find_items({"$and":[
                                                {"code": code}, 
                                                {"status": "buy_completed"}
                                            ]}, 
                                                "stocklab_demo", "order"))
    """매도 주문
    """
    for buy_completed_order in buy_completed_order_list:
        buy_price = buy_completed_order["매수완료"]["주문가격"]
        buy_order_no = buy_completed_order["매수완료"]["주문번호"]
        tick_size = ebest_demo.get_tick_size(int(buy_price))
        print("tick_size", tick_size)
        sell_price = int(buy_price) + tick_size*10
        sell_order = ebest_demo.order_stock(code, "2", str(sell_price), "1", "00")
        print("order_stock", sell_order)
        mongo.update_item({"매수완료.주문번호":buy_order_no}, 
                            {"$set":{"매도주문":sell_order[0], "status":"sell_ordered"}}, 
                        "stocklab_demo", "order")

def check_buy_order(code):
    """매수주문 완료 체크
    """
    order_list = list(mongo.find_items({"$and":[
                                            {"code": code}, 
                                            {"status":"buy_ordered"}]
                                        }, 
                                        "stocklab_demo", "order"))
    for order in order_list:
        time.sleep(1)
        code = order["code"]
        order_no = order["매수주문"]["주문번호"]
        order_cnt = order["매수주문"]["실물주문수량"]
        check_result = ebest_demo.order_check(order_no)
        print("check buy order result", check_result)
        result_cnt = check_result["체결수량"]
        if order_cnt == result_cnt:
            mongo.update_item({"매수주문.주문번호":order_no}, 
                                {"$set":{"매수완료":check_result, "status":"buy_completed"}}, 
                            "stocklab_demo", "order")
            print("매수완료", check_result)
    return len(order_list)

def check_sell_order(code):
    """매도주문 완료 체크"""
    sell_order_list = list(mongo.find_items({"$and":[
                                            {"code": code}, 
                                            {"status": "sell_ordered"}
                                        ]}, 
                                            "stocklab_demo", "order"))        
    for order in sell_order_list:
        time.sleep(1)
        code = order["code"]
        order_no = order["매도주문"]["주문번호"]
        order_cnt = order["매도주문"]["실물주문수량"]
        check_result = ebest_demo.order_check(order_no)
        print("check sell order result", check_result)
        result_cnt = check_result["체결수량"]
        if order_cnt == result_cnt:
            mongo.update_item({"매도주문.주문번호":order_no}, 
                            {"$set":{"매도완료":check_result, "status":"sell_completed"}}, 
                            "stocklab_demo", "order")
            print("매도완료", check_result)
    return len(sell_order_list)
  
def trading_scenario(code_list):
    for code in code_list:
        time.sleep(1)
        print(code)
        result = ebest_demo.get_current_call_price_by_code(code)
        current_price = result[0]["현재가"]
        print("current_price", current_price)
        """매수주문 체결확인
        """
        buy_order_cnt = check_buy_order(code)
        check_buy_completed_order(code)
        if buy_order_cnt == 0:
            """종목을 보유하고 있지 않는 경우 매수
            """
            order = ebest_demo.order_stock(code, "2", current_price, "2", "00")
            print("order_stock", order)
            order_doc = order[0]
            mongo.insert_item({"매수주문":order_doc, "code":code, "status": "buy_ordered"}, 
                            "stocklab_demo", "order")
        check_sell_order(code)

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    day = datetime.now() - timedelta(days=4)
    today = day.strftime("%Y%m%d")
    code_list = ["180640", "005930", "091990"]
    print("today:", today)
    scheduler.add_job(func=run_process_trading_scenario, 
        trigger="interval", minutes=5, id="demo", 
        kwargs={"code_list":code_list})
    scheduler.start()
    while True:
        print("waiting...", datetime.now())
        time.sleep(1)