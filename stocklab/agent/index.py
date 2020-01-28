import configparser
import requests
import pandas as pd
import xml.etree.cElementTree as ET
import io
from bs4 import BeautifulSoup

class Index():
    EXCHAGE_RATE_DOLLAR_URL="http://www.index.go.kr/openApi/xml_stts.do?userId=%s&idntfcId=%s&statsCode=106801"

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.api_key = config["INDEX"]["api_key"]
        if self.api_key is None:
            raise Exception("Need to api key")
        pass
        self.user = config["INDEX"]["user"]

    def collect_exchange_rate_dollar(self):
        request_url = self.EXCHAGE_RATE_DOLLAR_URL % (self.user, self.api_key)
        result_xml = requests.get(request_url).content
        soup = BeautifulSoup(result_xml, 'lxml-xml')

        month_item = soup.find("표", {"주기":"월"}).find_all("분류1", {"이름":"원/달러"})
        one_dollar=[]
        for row in month_item[0]:
            if hasattr(row, "text"):
                one_dollar.append({"year":row["주기"][0:4], "month":row["주기"][4:6], "value":row.text})
        return one_dollar

    def collect_exchange_rate_jpy(self):
        request_url = self.EXCHAGE_RATE_DOLLAR_URL % (self.user, self.api_key)
        result_xml = requests.get(request_url).content
        soup = BeautifulSoup(result_xml, 'lxml-xml')

        month_item = soup.find("표", {"주기":"월"}).find_all("분류1", {"이름":"원/100엔"})
        one_jpy=[]
        for row in month_item[0]:
            if hasattr(row, "text"):
                one_jpy.append({"year":row["주기"][0:4], "month":row["주기"][4:6], "value":row.text})
        return one_jpy
