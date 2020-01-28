import unittest
from stocklab.agent.ebest import EBest
import inspect
import time

class TestEbest(unittest.TestCase):
    def setUp(self):
        self.ebest = EBest("DEMO")
        self.ebest.login()

    def test_get_current_call_price_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_current_call_price_by_code("005930")
        assert result
        print(result)


    """
    def test_get_stock_price_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_stock_price_by_code("005930", "30")
        assert result is not None
        print(result)
    def testLogin(self):
        print(inspect.stack()[0][3])
        self.ebest.login()
        assert self.ebest.xa_session_client.login_state == 1

    def test_get_code_list(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_code_list("ALL")
        assert result is not None
        print(len(result))

    def test_get_stock_price_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_stock_price_by_code("005930", "2")
        assert result is not None
        print(result)

    def test_get_credit_trend_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_credit_trend_by_code("005930", "20190304")
        assert result is not None
        print(result)

    def test_get_short_trend_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_short_trend_by_code("005930", sdate="20190304", edate="20190304")
        assert result is not None
        print(result)

    def test_get_agent_trend_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_agent_trend_by_code("005930", fromdt="20190304", todt="20190304")
        assert result is not None
        print(result)

    def test_order_stock(self):
        print(inspect.stack()[0][3])
        result = self.ebest.order_stock("005930", "2", "46000", "2", "00")
        assert result
        print(result)
        #code = result[0]["ShtnIsuNo"]
        #order_no = result[0]["OrdNo"]
        #print(code, order_no)
        #time.sleep(1)
        #result1 = self.ebest.get_order_check("005930", order_no)
        #print(result1)



    def test_order_cancel(self):
        print(inspect.stack()[0][3])
        result = self.ebest.order_cancel("29515", "A005930", "2")
        assert result
        print(result)


    def test_get_price_n_min_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_price_n_min_by_code("20190412", "180640")
        assert result
        print(result)
    def test_get_price_n_min_by_code_tick(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_price_n_min_by_code("20190412", "005930", 0)
        assert result
        print(result)
    def test_get_account_stock_info(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_account_stock_info()
        assert result
        print(result)

    def test_get_account_info(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_account_info()
        assert result
        print(result)
    def test_real_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest._execute_real("005930")
        print(result)

    def test_order_check(self):
        print(inspect.stack()[0][3])
        result = self.ebest.order_check("29515")
        assert result
        print(result)

    def test_get_theme_by_code(self):
        time.sleep(1)
        print(inspect.stack()[0][3]) 
        result = self.ebest.get_theme_by_code("078020")
        assert result is not None
        print(len(result))

    def test_get_theme_list(self):
        time.sleep(1)
        print(inspect.stack()[0][3]) 
        result = self.ebest.get_theme_list()
        assert result is not None
        print(result)

    def test_get_category_list(self):
        time.sleep(1)
        print(inspect.stack()[0][3]) 
        result = self.ebest.get_category_list()
        assert result is not None
        print(len(result))

    def test_price_by_category(self):
        result = self.ebest.get_price_by_category("101")
        assert result is not None
        print(len(result))

    def test_price_by_theme(self):
        result = self.ebest.get_price_by_theme("0403")
        assert result is not None
        print(len(result))


    def test_short_trend_by_code(self):
        result = self.ebest.get_short_trend_by_code("0403", sdate="20181201", edate="20181203")
        assert result is not None
        print(len(result))

    def test_get_event_by_code(self):
        result = self.ebest.get_event_by_code("0403", date="20181201")
        assert result is not None
        print(len(result))

    def test_get_trade_history(self):
        result = self.ebest.get_trade_history("10")
        assert result is not None
        print(result)

    def test_get_account_info(self):
        result = self.ebest.get_account_info()
        assert result is not None
        print(result)

    def test_get_account_stock_info(self):
        result = self.ebest.get_account_stock_info()
        assert result is not None
        print(result)
    """

    def tearDown(self):
        self.ebest.logout()

