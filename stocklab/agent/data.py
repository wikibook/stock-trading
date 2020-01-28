import requests
import configparser
import xml.etree.ElementTree as ET

class Data():
    CORP_CODE_URL = "http://api.seibro.or.kr/openapi/service/CorpSvc/getIssucoCustnoByNm"
    CORP_INFO_URL = "http://api.seibro.or.kr/openapi/service/CorpSvc/getIssucoBasicInfo"
    STOCK_DISTRIBUTION_URL = "http://api.seibro.or.kr/openapi/service/CorpSvc/getStkDistributionStatus"

    def __init__(self):
        config = configparser.RawConfigParser()
        config.read('conf/config.ini')
        self.api_key = config["DATA"]["api_key"]
        if self.api_key is None:
            raise Exception("Need to api key")

    def get_corp_code(self, name=None):
        """
        한국예탁결제원에서 제공하는 기업코드를 회사명칭으로 검색합니다.
        :param name:str 회사명칭 ex) 삼성전자, 삼성 등
        :return result:dict 회사코드와 명칭을 반환합니다.
        """
        query_params = {"serviceKey":self.api_key,
                        "issucoNm": name,
                        "numOfRows": str(5000)}
        request_url =self.CORP_CODE_URL+"?"
        for k, v in query_params.items():
            request_url = request_url + k + "=" + v +"&"
        print(request_url)
        res = requests.get(request_url[:-1])
        root = ET.fromstring(res.text)
        from_tags = root.iter("items")
        result = {}
        for items in from_tags:
            for item in items.iter('item'):
                if name in item.find('issucoNm').text.split():
                    result["issucoCustno"] = item.find('issucoCustno').text
                    result["issucoNm"] = item.find('issucoNm').text
        return result

    def get_corp_info(self, code=None):
        """
        기업기본정보 기업개요 조회 API입니다.
        :param code:str 숫자로 관리되며 발행회사번호 조회에서 확인
        :return result:dict 기업개요 정보를 반환합니다.
        """
        query_params = {"serviceKey":self.api_key,
                        "issucoCustno": code}
        request_url =self.CORP_INFO_URL+"?"
        for k, v in query_params.items():
            request_url = request_url + k + "=" + v +"&"
        print(request_url)
        res = requests.get(request_url[:-1])
        root = ET.fromstring(res.text)
        from_tags = root.iter("item")
        result = {} 
        for item in from_tags:
            result["apliDt"] = item.find('apliDt').text
            result["bizno"] = item.find('bizno').text
            result["ceoNm"] = item.find('ceoNm').text
            result["engCustNm"] = item.find('engCustNm').text
            result["foundDt"] = item.find('founDt').text
            result["homepAddr"] = item.find('homepAddr').text
            result["pval"] = item.find('pval').text
            result["totalStkcnt"] = item.find('totalStkCnt').text
        return result     

    def get_stk_distribution_info(self, code=None, date=None):
        """
        주식분포내역 주주별 현황 조회 API입니다.
        :param code:str 숫자로 관리되며 발행회사번호 조회에서 확인
        :param data:str 기준일 8자리로 YYYYMMDD 형식으로 입력합니다. ex) 20181231 
        :return result_list:list 주주별 주식보유 현황 정보를 반환합니다.
        """
        query_params = {"serviceKey": self.api_key,
                        "issucoCustno": code,
                        "rgtStdDt": date}

        request_url =self.STOCK_DISTRIBUTION_URL+"?"
        for k, v in query_params.items():
            request_url = request_url + k + "=" + v +"&"
        print(request_url)
        res = requests.get(request_url[:-1])
        root = ET.fromstring(res.text)
        from_tags = root.iter("items")
        result_list = []
        for items in from_tags:
            for item in items.iter('item'):
                result = {}
                result["shrs"] = item.find('shrs').text
                result["shrs_ratio"] = item.find('shrsRatio').text
                result["stk_dist_name"] = item.find('stkDistbutTpnm').text
                result["stk_qty"] = item.find('stkqty').text
                result["stk_qty_ratio"] = item.find('stkqtyRatio').text
                result_list.append(result)
        return result_list