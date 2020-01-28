import os
from api_server import app
import unittest
import tempfile
import json
import inspect

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_get_codes(self):
        print(inspect.stack()[0][3])
        rv = self.app.get("/codes")
        result = rv.get_json()
        print(len(result["code_list"]))
        assert rv.status_code == 200 and len(result["code_list"]) > 0 

    def test_get_codes_with_parameter(self):
        print(inspect.stack()[0][3])
        rv = self.app.get("/codes?market=2")
        result = rv.get_json()
        print(len(result["code_list"]))
        assert rv.status_code == 200 and len(result["code_list"]) > 0

    def test_get_code(self):
        print(inspect.stack()[0][3])
        rv = self.app.get("/codes/005930")
        print(rv.data, rv.status_code)
        assert rv.status_code == 200

    def test_get_price(self):
        print(inspect.stack()[0][3])
        rv = self.app.get("/codes/002170/price")
        assert rv.status_code == 200

    def test_get_price_with_parameter(self):
        print(inspect.stack()[0][3])
        rv = self.app.get("/codes/002170/price?start_date=20190228&end_date=20190228")
        result = rv.get_json()
        print(result["count"])
        assert rv.status_code == 200

    def test_get_order_list(self):
        print(inspect.stack()[0][3])
        rv = self.app.get("/orders?status=buy_ordered")
        result = rv.get_json()
        print(result)
        assert rv.status_code == 200

    def tearDown(self):
        pass
