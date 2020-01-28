import unittest
from stocklab.agent.index import Index
import inspect

class TestIndex(unittest.TestCase):

    def setUp(self):
        self.index = Index()

    def test_collect_exchange_rate_dollar(self):
        print(inspect.stack()[0][3])
        result = self.index.collect_exchange_rate_dollar()
        assert result
        print(result)

    def test_collect_exchange_rate_jpy_(self):
        print(inspect.stack()[0][3])
        result = self.index.collect_exchange_rate_jpy()
        assert result
        print(result)


    def tearDown(self):
        pass