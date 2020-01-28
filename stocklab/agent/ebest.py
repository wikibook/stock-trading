import configparser
import win32com.client
import pythoncom
from datetime import datetime
import time

class XASession:
    #로그인 상태를 확인하기 위한 클래스변수
    login_state = 0

    def OnLogin(self, code, msg):
        """
        로그인 시도 후 호출되는 이벤트.
        code가 0000이면 로그인 성공
        """
        if code == "0000":
            print(code, msg)
            XASession.login_state = 1
        else:
            print(code, msg)

    def OnDisconnect(self):
        """
        서버와 연결이 끊어지면 발생하는 이벤트
        """
        print("Session disconntected")
        XASession.login_state = 0


class XAQuery:
    RES_PATH ="C:\\eBEST\\xingAPI\\Res\\"
    tr_run_state = 0

    def OnReceiveData(self, code):
        print("OnReceiveData", code)
        XAQuery.tr_run_state = 1

    def OnReceiveMessage(self, error, code, message):
        print("OnReceiveMessage", error, code, message, XAQuery.tr_run_state)

class XAReal:
    RES_PATH = "C:\\eBEST\\xingAPI\\Res\\"

    def register_code(self, code):
        print("register code", code)
        self.LoadFromResFile(XAReal.RES_PATH + "K3_.res")
        self.SetFieldData("InBlock", "shcode", code)
        self.AdviseRealData()

    def OnReceiveRealData(self, tr_code):
        print("tr_code", tr_code)
        result = []
        for field in ["chetime", "sign", "change", "drate", "price", "opentime", "open",
                      "hightime", "high", "lowtime", "low", "cgubun", "cvolume", "volume",
                      "mdvolume", "mdchecnt", "msvolume", "mschecnt", "cpower", "w_avrg",
                      "offerho", "bidho", "status", "jnilvolume", "shcode"]:
            value = self.GetFieldData("OutBlock", field)
            item[field] = value
            result.append(item)
        print(result)

class EBest:
    QUERY_LIMIT_10MIN = 200
    LIMIT_SECONDS = 600 #10min

    def __init__(self, mode=None):
        """
        config.ini 파일을 로드해 사용자, 서버정보 저장
        query_cnt는 10분당 200개 TR 수행을 관리하기 위한 리스트
        xa_session_client는 XASession 객체
        :param mode:str - 모의서버는 DEMO 실서버는 PROD로 구분
        """
        if mode not in ["PROD", "DEMO", "ACE"]:
            raise Exception("Need to run_mode(PROD or DEMO or ACE)")

        run_mode = "EBEST_" + mode
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.user = config[run_mode]['user']
        self.passwd = config[run_mode]['password']
        self.cert_passwd = config[run_mode]['cert_passwd']
        self.host = config[run_mode]['host']
        self.port = config[run_mode]['port']
        self.account = config[run_mode]['account']

        self.xa_session_client = win32com.client.DispatchWithEvents("XA_Session.XASession", XASession)

        self.query_cnt = []

    def login(self):
        self.xa_session_client.ConnectServer(self.host, self.port)
        self.xa_session_client.Login(self.user, self.passwd, self.cert_passwd, 0, 0)
        while XASession.login_state == 0:
            pythoncom.PumpWaitingMessages()

    def logout(self):
        XASession.login_state = 0
        self.xa_session_client.DisconnectServer()

    def _execute_query(self, res, in_block_name, out_block_name, *out_fields, **set_fields):
        """TR코드를 실행하기 위한 메소드입니다.
        :param res:str 리소스명(TR)
        :param in_block_name:str 인블록명
        :param out_blcok_name:str 아웃블록명
        :param out_params:list 출력필드 리스트
        :param in_params:dict 인블록에 설정할 필드 딕셔너리
        :return result:list 결과를 list에 담아 반환 
        """
        time.sleep(1)
        print("current query cnt:", len(self.query_cnt))
        print(res, in_block_name, out_block_name)
        while len(self.query_cnt) >= EBest.QUERY_LIMIT_10MIN:
            time.sleep(1)
            print("waiting for execute query... current query cnt:", len(self.query_cnt))
            self.query_cnt = list(filter(lambda x: (datetime.today() - x).total_seconds() < EBest.LIMIT_SECONDS, self.query_cnt))

        xa_query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQuery)
        xa_query.LoadFromResFile(XAQuery.RES_PATH + res+".res")

        #in_block_name 셋팅
        for key, value in set_fields.items():
            xa_query.SetFieldData(in_block_name, key, 0, value)
        errorCode = xa_query.Request(0)

        #요청 후 대기
        waiting_cnt = 0
        while xa_query.tr_run_state == 0:
            waiting_cnt +=1
            if waiting_cnt % 1000000 == 0 :
                print("Waiting....", self.xa_session_client.GetLastError())
            pythoncom.PumpWaitingMessages()

        #결과블럭 
        result = []
        count = xa_query.GetBlockCount(out_block_name)

        for i in range(count):
            item = {}
            for field in out_fields:
                value = xa_query.GetFieldData(out_block_name, field, i)
                item[field] = value
            result.append(item)

        """
        print("IsNext?", xa_query.IsNext)
        while xa_query.IsNext == True:
            time.sleep(1)
            errorCode = xa_query.Request(1)
            print("errorCode", errorCode)
            if errorCode < 0:
                break
            count = xa_query.GetBlockCount(out_block_name)
            print("count", count)
            if count == 0:
                break
            for i in range(count):
                item = {}
                for field in out_fields:
                    value = xa_query.GetFieldData(out_block_name, field, i)
                    item[field] = value
                print(item)
                result.append(item)
        """
        XAQuery.tr_run_state = 0
        self.query_cnt.append(datetime.today())

        #영문필드를 한글필드명으로 변환
        for item in result:
            for field in list(item.keys()):
                if getattr(Field, res, None):
                    res_field = getattr(Field, res, None)
                    if out_block_name in res_field:
                        field_hname = res_field[out_block_name]
                        if field in field_hname:
                            item[field_hname[field]] = item[field]
                            item.pop(field)
        return result

    def get_tick_size(self, price):
        """호가 단위 조회 메소드
        참고:    
        http://regulation.krx.co.kr/contents/RGL/03/03010100/RGL03010100.jsp#8339ae36256c1f6cffd910cd71e4dc85=3
        http://regulation.krx.co.kr/contents/RGL/03/03020100/RGL03020100.jsp
 
        :param price:int 가격
        :return 호가 단위
        """
        if price < 1000: return 1
        elif price >=1000 and price < 5000: return 5
        elif price >=5000 and price < 10000: return 10
        elif price >=10000 and price < 50000: return 50
        elif price >=50000 and price < 100000: return 100
        elif price >=100000 and price < 500000: return 500
        elif price >=500000: return 1000

    def get_current_call_price_by_code(self, code=None):
        """TR: t1101 주식 현재가 호가 조회
        :param code:str 종목코드
        """
        tr_code = "t1101"
        in_params = {"shcode": code}
        out_params =["hname", "price", "sign", "change", "diff", "volume", 
            "jnilclose", "offerho1","bidho1", "offerrem1", "bidrem1",
            "offerho2","bidho2", "offerrem2", "bidrem2",
            "offerho3","bidho3", "offerrem3", "bidrem3",
            "offerho4","bidho4", "offerrem4", "bidrem4",
            "offerho5","bidho5", "offerrem5", "bidrem5",
            "offerho6","bidho6", "offerrem6", "bidrem6",
            "offerho7","bidho7", "offerrem7", "bidrem7",
            "offerho8","bidho8", "offerrem8", "bidrem8",
            "offerho9","bidho9", "offerrem9", "bidrem9",
            "offerho10","bidho10", "offerrem10", "bidrem10",
            "preoffercha10", "prebidcha10", "offer", "bid",
            "preoffercha", "prebidcha", "hotime", "yeprice", "yevolume",
            "yesign", "yechange", "yediff", "tmoffer", "tmbid", "ho_status",
            "shcode", "uplmtprice", "dnlmtprice", "open", "high", "low"]

        result = self._execute_query("t1101", 
                                "t1101InBlock", 
                                "t1101OutBlock",
                                *out_params,
                                **in_params)

        for item in result:
            item["code"] = code

        return result
 
    def get_stock_price_by_code(self, code=None, cnt="1"):
        """TR: t1305 현재 날짜를 기준으로 cnt 만큼 전일의 데이터를 가져온다
        :param code:str 종목코드
        :param cnt:str 데이터 범위
        :return result:list 종목의 최근 가격 정보
        """
        tr_code = "t1305"
        in_params = {"shcode":code, "dwmcode": "1", "date":"", "idx":"", "cnt":cnt}
        out_params =['date', 'open', 'high', 'low', 'close', 'sign', 
                    'change', 'diff', 'volume', 'diff_vol', 'chdegree', 
                    'sojinrate', 'changerate', 'fpvolume', 'covolume', 
                    'value', 'ppvolume', 'o_sign', 'o_change', 'o_diff', 
                    'h_sign', 'h_change', 'h_diff', 'l_sign', 'l_change', 
                    'l_diff', 'marketcap'] 
        #t8413
        #in_params = {"shcode":code, "qrycnt": "1", "gubun":"2", "sdate":start, "cts_date":"", "edate":end, "comp_yn":"N"}    
        #out_params =['date', 'open', 'high', 'low', 'close', 'jdiff_vol', 'sign'] 
        result = self._execute_query("t1305", 
                                "t1305InBlock", 
                                "t1305OutBlock1",
                                *out_params,
                                **in_params)

        for item in result:
            item["code"] = code

        return result
        
    def get_code_list(self, market=None):
        """TR: t8436 코스피, 코스닥의 종목 리스트를 가져온다
        :param market:str 전체(0), 코스피(1), 코스닥(2)
        :return result:list 시장 별 종목 리스트
        """
        if market not in ["ALL", "KOSPI", "KOSDAQ"]:
            raise Exception("Need to market param(ALL, KOSPI, KOSDAQ)")

        market_code = {"ALL":"0", "KOSPI":"1", "KOSDAQ":"2"}
        in_params = {"gubun":market_code[market]}
        out_params =['hname', 'shcode', 'expcode', 'etfgubun', 'memedan', 'gubun', 'spac_gubun'] 
        result = self._execute_query("t8436", 
                                "t8436InBlock", 
                                "t8436OutBlock",
                                *out_params,
                                **in_params)
        return result

    def get_credit_trend_by_code(self, code=None, date=None):
        """TR: t1921 신용거래동향 
        :param code:str 종목코드
        :param date:str 날짜 8자리 ex) 20190222
        """
        in_params = {"gubun":"0", "shcode":code, "date":date, "idx":"0"}
        out_params =["mmdate", "close", "sign", "jchange", "diff", "nvolume",
                    "svolume", "jvolume", "price", "change", "gyrate", "jkrate"
                    "shcode"]

        result = self._execute_query("t1921",
                                    "t1921InBlock",
                                    "t1921OutBlock1",
                                    *out_params,
                                    **in_params)
        for item in result:
            item["code"] = code

        return result


    def get_agent_trend_by_code(self, code=None ,fromdt=None, todt=None):
        """TR: t1717 외인기관별 종목별 동향
        :param code:str 종목코드
        :param fromdt:str 조회 시작 날짜
        :param todt:str 조회 종료 날짜
        :return result:list 시장 별 종목 리스트
        """
        in_params = {"gubun":"0", "fromdt":fromdt, "todt":todt, "shcode":code}
        out_params =["date", "close", "sign", "change", "diff", "volume", 
                    "tjj0000_vol", "tjj0001_vol", "tjj0002_vol", "tjj0003_vol",
                    "tjj0004_vol", "tjj0005_vol","tjj0006_vol", "tjj0007_vol",
                    "tjj0008_vol", "tjj0009_vol", "tjj0010_vol", "tjj0011_vol",
                    "tjj0018_vol", "tjj0016_vol", "tjj0017_vol", "tjj0001_dan",
                    "tjj0002_dan", "tjj0003_dan", "tjj0004_dan", "tjj0005_dan",
                    "tjj0006_dan", "tjj0007_dan", "tjj0008_dan", "tjj0009_dan",
                    "tjj0010_dan", "tjj0011_dan", "tjj0018_dan", "tjj0016_dan",
                    "tjj0017_dan" ] 
        result = self._execute_query("t1717",
                                    "t1717InBlock",
                                    "t1717OutBlock",
                                    *out_params,
                                    **in_params)
        for item in result:
            item["code"] = code

        return result

    def get_short_trend_by_code(self, code=None, sdate=None, edate=None):
        """TR: t1927 공매도일별추이
        :param code:str 종목코드
        :param sdate:str 시작일자 
        :param edate:str 종료일자
        :return result:list 시장 별 종목 리스트
        """
        in_params = {"date":sdate, "sdate":sdate, "edate":edate, "shcode":code}
        out_params =["date", "price", "sign", "change", "diff", "volume", "value", 
                    "gm_vo", "gm_va", "gm_per", "gm_avg", "gm_vo_sum"]

        result = self._execute_query("t1927",
                                    "t1927InBlock",
                                    "t1927OutBlock1",
                                    *out_params,
                                    **in_params)

        for item in result:
            item["code"] = code

        return result

    def get_theme_by_code(self, code):
        if code is None:
            raise Exception("Need to code param")

        in_params = {"shcode":code}
        out_params =['tmname', 'tmcode'] 
        result = self._execute_query("t1532", 
                                "t1532InBlock", 
                                "t1532OutBlock",
                                *out_params,
                                **in_params)
        return result

    def get_theme_list(self):
        in_params = {"dummy":"1"}
        out_params =['tmname', 'tmcode'] 
        result = self._execute_query("t8425", 
                                "t8425InBlock", 
                                "t8425OutBlock",
                                *out_params,
                                **in_params)
        return result

    def get_category_list(self):
        in_params = {"gubun1":"1"}
        out_params =['hname', 'upcode'] 
        result = self._execute_query("t8424", 
                                "t8424InBlock", 
                                "t8424OutBlock",
                                *out_params,
                                **in_params)
        return result
    
    def get_price_by_category(self, upcode=None):
        if upcode is None:
            raise Exception("Need to upcode")
        in_params = {"gubun":"0", "upcode":upcode}
        out_params =['hname', 'price', 'sign', 'change', 'diff', 
                    'volume', 'open', 'high', 'low', 'perx', 
                    'frgsvolume', 'orgsvolume', 'diff_vol', 'total', 
                    'value', 'shcode'] 
        result = self._execute_query("t1516",
                                    "t1516InBlock",
                                    "t1516OutBlock1",
                                    *out_params,
                                    **in_params)
        return result

    def get_price_by_theme(self, tmcode=None):
        if tmcode is None:
            raise Exception("Need to tmcode")
        in_params = {"tmcode":tmcode}
        out_params =['hname', 'price', 'sign', 'change', 'diff', 'shcode'
                    'volume', 'open', 'high', 'low', 'value'] 
        result = self._execute_query("t1537",
                                    "t1537InBlock",
                                    "t1537OutBlock1",
                                    *out_params,
                                    **in_params)
        return result




    def get_event_by_code(self, code=None, date=None):
        if code is None:
            raise Exception("Need to tmcode")
        in_params = {"shcode":code, "date":date}
        out_params =["recdt", "tableid", "upgu", 
                    "custno", "custnm", "shcode", "upnm" ]
        result = self._execute_query("t3202",
                                    "t3202InBlock",
                                    "t3202OutBlock",
                                    *out_params,
                                    **in_params)
        return result

    def get_trade_history(self, count=None):
        in_params = {"RecCnt": count, "AcntNo": self.account, "Pwd": self.passwd,
                     "QrySrtDt":"20181201", "QryEndDt":"20181205"}
        out_params =["recdt", "tableid", "upgu", 
                    "custno", "custnm", "shcode", "upnm" ]
        result = self._execute_query("CDPCQ04700",
                                    "CDPCQ04700InBlock1",
                                    "CDPCQ04700OutBlock1",
                                    *out_params,
                                    **in_params)
        return result

    def get_account_info(self):
        """TR: CSPAQ12200 현물계좌 예수금/주문가능금액/총평가
        :return result:list Field CSPAQ12200 참고
        """
        in_params = {"RecCnt":"1", "AcntNo": self.account, "Pwd": self.passwd}
        out_params =["MnyOrdAbleAmt", "BalEvalAmt", "DpsastTotamt", 
                    "InvstOrgAmt", "InvstPlAmt", "Dps"]
        result = self._execute_query("CSPAQ12200",
                                    "CSPAQ12200InBlock1",
                                    "CSPAQ12200OutBlock2",
                                    *out_params,
                                    **in_params)
        return result

    def get_account_stock_info(self):
        """TR: CSPAQ12300 현물계좌 잔고내역 조회
        :return result:list 계좌 보유 종목 정보
        """
        in_params = {"RecCnt": "1", "AcntNo": self.account, "Pwd": self.passwd, "BalCreTp": "0", "CmsnAppTpCode": "0", "D2balBaseQryTp": "0", "UprcTpCode": "0"}
        out_params =["IsuNo", "IsuNm", "BnsBaseBalQty", "SellPrc", "BuyPrc", "NowPrc", "AvrUprc", "PnlRat", "BalEvalAmt"]
        result = self._execute_query("CSPAQ12300",
                                    "CSPAQ12300InBlock1",
                                    "CSPAQ12300OutBlock3",
                                    *out_params,
                                    **in_params)
        return result


    def order_check(self, order_no=None):
        """TR: t0425 주식 체결/미체결
        :param code:str 종목코드
        :param order_no:str 주문번호
        :return result:dict 주문번호의 체결상태
        """
        in_params = {"accno": self.account, "passwd": self.passwd, "expcode": "", 
                    "chegb":"0", "medosu":"0", "sortgb":"1", "cts_ordno":" "}
        out_params = ["ordno", "expcode", "medosu", "qty", "price", "cheqty", "cheprice", "ordrem", "cfmqty", "status", "orgordno", "ordgb", "ordermtd", "sysprocseq", "hogagb", "price1", "orggb", "singb", "loandt"]
        result_list = self._execute_query("t0425",
                                    "t0425InBlock",
                                    "t0425OutBlock1",
                                    *out_params,
                                    **in_params)
        
        result = {}
        if order_no is not None:
            for item in result_list:
                if item["주문번호"] == order_no:
                    result = item
            return result
        else:
            return result_list

    def order_check2(self, date, code, order_no=None):
        #CSPAQ13700
        print("get_order_check, ", order_no)
        in_params = {"RecCnt":"1", "AcntNo":self.account, "InptPwd":self.passwd, "OrdMktCode":"00", 
                    "BnsTpCode":"0", "IsuNo":code, "ExecYn":"0", "OrdDt":date, "SrtOrdNo2":"0", 
                    "BkseqTpCode":"0", "OrdPtnCode":"00"}

        out_params_3 = ["OrdDt", "OrdMktCode", "OrdNo", "OrgOrdNo", "IsuNo", 
                     "IsuNm", "BnsTpCode", "BnsTpNm", "OrdPtnCode", "OrdPtnNm", 
                     "MrcTpCode", "OrdQty", "OrdPrc", "ExecQty", "ExecPrc", "LastExecTime", 
                     "OrdprcPtnCode", "OrdprcPtnNm", "AllExecQty", "OrdTime"]
        result_list = self._execute_query("CSPAQ13700",
                                    "CSPAQ13700InBlock1",
                                    "CSPAQ13700OutBlock3",
                                    *out_params_3,
                                    **in_params)
        
        result = {}
        print("get_order_check result len", len(result_list))
        if order_no is not None:
            for item in result_list:
                if item["주문번호"] == order_no:
                    result = item
            return result
        else:
            return result_list

    def order_stock(self, code, qty, price, bns_type, order_type="00"):
        """TR: CSPAT00600 현물 정상 주문
        :param bns_type:str 매매타입, 1:매도, 2:매수
        :prarm order_type:str 호가유형, 
            00:지정가, 03:시장가, 05:조건부지정가, 07:최우선지정가
            61:장개시전시간외 종가, 81:시간외종가, 82:시간외단일가
        :return result:dict 주문 관련정보
        """
        in_params = {"AcntNo":self.account, "InptPwd":self.passwd, "IsuNo":code, "OrdQty":qty,
                    "OrdPrc":price, "BnsTpCode":bns_type, "OrdprcPtnCode":order_type, "MgntrnCode":"000",
                    "LoanDt":"", "OrdCndiTpCode":"0"}
        out_params = ["OrdNo", "OrdTime", "OrdMktCode", "OrdPtnCode", "ShtnIsuNo", "MgempNo", "OrdAmt", "SpotOrdQty", "IsuNm"]

        result = self._execute_query("CSPAT00600",
                                    "CSPAT00600InBlock1",
                                    "CSPAT00600OutBlock2",
                                    *out_params,
                                    **in_params)
        return result

    def order_cancel(self, order_no, code, qty):
        """TR: CSPAT00800 현물 취소주문
        :param order_no:str 주문번호
        :param code:str 종목코드
        :param qty:str 취소 수량
        :return result:dict 취소 결과
        """
        in_params = {"OrgOrdNo":order_no,"AcntNo":self.account, "InptPwd":self.passwd, "IsuNo":code, "OrdQty":qty}
        out_params = ["OrdNo", "PrntOrdNo", "OrdTime", "OrdPtnCode", "ShtnIsuNo", "IsuNm"]

        result = self._execute_query("CSPAT00800",
                                    "CSPAT00800InBlock1",
                                    "CSPAT00800OutBlock2",
                                    *out_params,
                                    **in_params)
        return result

    def get_price_n_min_by_code(self, date, code, tick=None):
        """TR: t8412 주식차트(N분) 
        :param code:str 종목코드
        :param date:str 시작시간
        :return result:dict 하루치 분당 가격 정보
        """
        in_params = {"shcode":code,"ncnt":"1", "qrycnt":"500", "nday":"1", "sdate":date, 
                "stime":"090000", "edate":date, "etime":"153000", "cts_date":"00000000", 
                "cts_time":"0000000000", "comp_yn":"N"}
        out_params = ["date", "time", "open", "high", "low", "close", "jdiff_vol", "value"]

        result_list = self._execute_query("t8412",
                                    "t8412InBlock",
                                    "t8412OutBlock1",
                                    *out_params,
                                    **in_params)
        result = {}
        for idx, item in enumerate(result_list):
            result[idx] = item
        if tick is not None:
            return result[tick]
        return result

class Field:
    t1101 = {
        "t1101OutBlock":{
            "hname":"한글명",
            "price":"현재가",
            "sign":"전일대비구분",
            "change":"전일대비",
            "diff":"등락율",
            "volume":"누적거래량",
            "jnilclose":"전일종가",
            "offerho1":"매도호가1",
            "bidho1":"매수호가1",
            "offerrem1":"매도호가수량1",
            "bidrem1":"매수호가수량1",
            "preoffercha1":"직전매도대비수량1",
            "prebidcha1":"직전매수대비수량1",
            "offerho2":"매도호가2",
            "bidho2":"매수호가2",
            "offerrem2":"매도호가수량2",
            "bidrem2":"매수호가수량2",
            "preoffercha2":"직전매도대비수량2",
            "prebidcha2":"직전매수대비수량2",
            "offerho3":"매도호가3",
            "bidho3":"매수호가3",
            "offerrem3":"매도호가수량3",
            "bidrem3":"매수호가수량3",
            "preoffercha3":"직전매도대비수량3",
            "prebidcha3":"직전매수대비수량3",
            "offerho4":"매도호가4",
            "bidho4":"매수호가4",
            "offerrem4":"매도호가수량4",
            "bidrem4":"매수호가수량4",
            "preoffercha4":"직전매도대비수량4",
            "prebidcha4":"직전매수대비수량4",
            "offerho5":"매도호가5",
            "bidho5":"매수호가5",
            "offerrem5":"매도호가수량5",
            "bidrem5":"매수호가수량5",
            "preoffercha5":"직전매도대비수량5",
            "prebidcha5":"직전매수대비수량5",
            "offerho6":"매도호가6",
            "bidho6":"매수호가6",
            "offerrem6":"매도호가수량6",
            "bidrem6":"매수호가수량6",
            "preoffercha6":"직전매도대비수량6",
            "prebidcha6":"직전매수대비수량6",
            "offerho7":"매도호가7",
            "bidho7":"매수호가7",
            "offerrem7":"매도호가수량7",
            "bidrem7":"매수호가수량7",
            "preoffercha7":"직전매도대비수량7",
            "prebidcha7":"직전매수대비수량7",
            "offerho8":"매도호가8",
            "bidho8":"매수호가8",
            "offerrem8":"매도호가수량8",
            "bidrem8":"매수호가수량8",
            "preoffercha8":"직전매도대비수량8",
            "prebidcha8":"직전매수대비수량8",
            "offerho9":"매도호가9",
            "bidho9":"매수호가9",
            "offerrem9":"매도호가수량9",
            "bidrem9":"매수호가수량9",
            "preoffercha9":"직전매도대비수량9",
            "prebidcha9":"직전매수대비수량9",
            "offerho10":"매도호가10",
            "bidho10":"매수호가10",
            "offerrem10":"매도호가수량10",
            "bidrem10":"매수호가수량10",
            "preoffercha10":"직전매도대비수량10",
            "prebidcha10":"직전매수대비수량10",
            "offer":"매도호가수량합",
            "bid":"매수호가수량합",
            "preoffercha":"직전매도대비수량합",
            "prebidcha":"직전매수대비수량합",
            "hotime":"수신시간",
            "yeprice":"예상체결가격",
            "yevolume":"예상체결수량",
            "yesign":"예상체결전일구분",
            "yechange":"예상체결전일대비",
            "yediff":"예상체결등락율",
            "tmoffer":"시간외매도잔량",
            "tmbid":"시간외매수잔량",
            "ho_status":"동시구분",
            "shcode":"단축코드",
            "uplmtprice":"상한가",
            "dnlmtprice":"하한가",
            "open":"시가",
            "high":"고가",
            "low":"저가"
        }
    }
    t1305 = {
        "t1305OutBlock1":{
            "date":"날짜",
            "open":"시가",
            "high":"고가",
            "low":"저가",
            "close":"종가",
            "sign":"전일대비구분",
            "change":"전일대비",
            "diff":"등락율",
            "volume":"누적거래량",
            "diff_vol":"거래증가율",
            "chdegree":"체결강도",
            "sojinrate":"소진율",
            "changerate":"회전율",
            "fpvolume":"외인순매수",
            "covolume":"기관순매수",
            "shcode":"종목코드",
            "value":"누적거래대금",
            "ppvolume":"개인순매수",
            "o_sign":"시가대비구분",
            "o_change":"시가대비",
            "o_diff":"시가기준등락율",
            "h_sign":"고가대비구분",
            "h_change":"고가대비",
            "h_diff":"고가기준등락율",
            "l_sign":"저가대비구분",
            "l_change":"저가대비",
            "l_diff":"저가기준등락율",
            "marketcap":"시가총액"
        }
    }

    t1921 = {
        "t1921OutBlock1":{
            "mmdate":"날짜",
            "close":"종가",
            "sign":"전일대비구분",
            "jchange":"전일대비",
            "diff":"등락율",
            "nvolume":"신규",
            "svolume":"상환",
            "jvolume":"잔고",
            "price":"금액",
            "change":"대비",
            "gyrate":"공여율",
            "jkrate":"잔고율",
            "shcode":"종목코드"
        }
    }

    t8436 = {
        "t8436OutBlock":{
            "hname":"종목명",
            "shcode":"단축코드",
            "expcode":"확장코드",
            "etfgubun":"ETF구분",
            "uplmtprice":"상한가",
            "dnlmtprice":"하한가",
            "jnilclose":"전일가",
            "memedan":"주문수량단위",
            "recprice":"기준가",
            "gubun":"시장구분",
            "bu12gubun":"증권그룹",
            "spac_gubun":"기업인수목적회사여부",
            "filler":"filler(미사용)"
        }
    }

    t1717 = {
        "t1717OutBlock":{
            "date":"일자",
            "close":"종가",
            "sign":"전일대비구분",
            "change":"전일대비",
            "diff":"등락율",
            "volume":"누적거래량",
            "tjj0000_vol":"사모펀드(순매수량)",
            "tjj0001_vol":"증권(순매수량)",
            "tjj0002_vol":"보험(순매수량)",
            "tjj0003_vol":"투신(순매수량)",
            "tjj0004_vol":"은행(순매수량)",
            "tjj0005_vol":"종금(순매수량)",
            "tjj0006_vol":"기금(순매수량)",
            "tjj0007_vol":"기타법인(순매수량)",
            "tjj0008_vol":"개인(순매수량)",
            "tjj0009_vol":"등록외국인(순매수량)",
            "tjj0010_vol":"미등록외국인(순매수량)",
            "tjj0011_vol":"국가외(순매수량)",
            "tjj0018_vol":"기관(순매수량)",
            "tjj0016_vol":"외인계(순매수량)(등록+미등록)",
            "tjj0017_vol":"기타계(순매수량)(기타+국가)",
            "tjj0000_dan":"사모펀드(단가)",
            "tjj0001_dan":"증권(단가)",
            "tjj0002_dan":"보험(단가)",
            "tjj0003_dan":"투신(단가)",
            "tjj0004_dan":"은행(단가)",
            "tjj0005_dan":"종금(단가)",
            "tjj0006_dan":"기금(단가)",
            "tjj0007_dan":"기타법인(단가)",
            "tjj0008_dan":"개인(단가)",
            "tjj0009_dan":"등록외국인(단가)",
            "tjj0010_dan":"미등록외국인(단가)",
            "tjj0011_dan":"국가외(단가)",
            "tjj0018_dan":"기관(단가)",
            "tjj0016_dan":"외인계(단가)(등록+미등록)",
            "tjj0017_dan":"기타계(단가)(기타+국가)"
        }
    }

    t1927 = {
        "t1927OutBlock1":{
            "date":"일자",
            "price":"현재가",
            "sign":"전일대비구분",
            "change":"전일대비",
            "diff":"등락율",
            "volume":"거래량",
            "value":"거래대금",
            "gm_vo":"공매도수량",
            "gm_va":"공매도대금",
            "gm_per":"공매도거래비중",
            "gm_avg":"평균공매도단가",
            "gm_vo_sum":"누적공매도수량"
        }
    }

    t0425 ={
        "t0425OutBlock1":{
            "ordno":"주문번호",
            "expcode":"종목번호",
            "medosu":"구분",
            "qty":"주문수량",
            "price":"주문가격",
            "cheqty":"체결수량",
            "cheprice":"체결가격",
            "ordrem":"미체결잔량",
            "cfmqty":"확인수량",
            "status":"상태",
            "orgordno":"원주문번",
            "ordgb":"유형",
            "ordtime":"주문시간",
            "ordermtd":"주문매체",
            "sysprocseq":"처리순번",
            "hogagb":"호가유형",
            "price1":"현재가",
            "orggb":"주문구분",
            "singb":"신용구분",
            "loandt":"대출일자"
        }
    }
    t8412 = {
        "t8412OutBlock1":{
            "date":"날짜",
            "time":"시간",
            "open":"시가",
            "high":"고가",
            "low":"저가",
            "close":"종가",
            "jdiff_vol":"거래량",
            "value":"거래대금",
            "jongchk":"수정구분",
            "rate":"수정비율",
            "sign":"종가등락구분"
        }
    }
    CSPAQ12200 = {
        "CSPAQ12200OutBlock2":{
            "RecCnt":"레코드갯수",
            "BrnNm":"지점명",
            "AcntNm":"계좌명",
            "MnyOrdAbleAmt":"현금주문가능금액",
            "MnyoutAbleAmt":"출금가능금액",
            "SeOrdAbleAmt":"거래소금액",
            "KdqOrdAbleAmt":"코스닥금액",
            "BalEvalAmt":"잔고평가금액",
            "RcvblAmt":"미수금액",
            "DpsastTotamt":"예탁자산총액",
            "PnlRat":"손익율",
            "InvstOrgAmt":"투자원금",
            "InvstPlAmt":"투자손익금액",
            "CrdtPldgOrdAmt":"신용담보주문금액",
            "Dps":"예수금",
            "SubstAmt":"대용금액",
            "D1Dps":"D1예수금",
            "D2Dps":"D2예수금",
            "MnyrclAmt":"현금미수금액",
            "MgnMny":"증거금현금",
            "MgnSubst":"증거금대용",
            "ChckAmt":"수표금액",
            "SubstOrdAbleAmt":"대용주문가능금액",
            "MgnRat100pctOrdAbleAmt":"증거금률100퍼센트주문가능금액",
            "MgnRat35ordAbleAmt":"증거금률35%주문가능금액",
            "MgnRat50ordAbleAmt":"증거금률50%주문가능금액",
            "PrdaySellAdjstAmt":"전일매도정산금액",
            "PrdayBuyAdjstAmt":"전일매수정산금액",
            "CrdaySellAdjstAmt":"금일매도정산금액",
            "CrdayBuyAdjstAmt":"금일매수정산금액",
            "D1ovdRepayRqrdAmt":"D1연체변제소요금액",
            "D2ovdRepayRqrdAmt":"D2연체변제소요금액",
            "D1PrsmptWthdwAbleAmt":"D1추정인출가능금액",
            "D2PrsmptWthdwAbleAmt":"D2추정인출가능금액",
            "DpspdgLoanAmt":"예탁담보대출금액",
            "Imreq":"신용설정보증금",
            "MloanAmt":"융자금액",
            "ChgAfPldgRat":"변경후담보비율",
            "OrgPldgAmt":"원담보금액",
            "SubPldgAmt":"부담보금액",
            "RqrdPldgAmt":"소요담보금액",
            "OrgPdlckAmt":"원담보부족금액",
            "PdlckAmt":"담보부족금액",
            "AddPldgMny":"추가담보현금",
            "D1OrdAbleAmt":"D1주문가능금액",
            "CrdtIntdltAmt":"신용이자미납금액",
            "EtclndAmt":"기타대여금액",
            "NtdayPrsmptCvrgAmt":"익일추정반대매매금액",
            "OrgPldgSumAmt":"원담보합계금액",
            "CrdtOrdAbleAmt":"신용주문가능금액",
            "SubPldgSumAmt":"부담보합계금액",
            "CrdtPldgAmtMny":"신용담보금현금",
            "CrdtPldgSubstAmt":"신용담보대용금액",
            "AddCrdtPldgMny":"추가신용담보현금",
            "CrdtPldgRuseAmt":"신용담보재사용금액",
            "AddCrdtPldgSubst":"추가신용담보대용",
            "CslLoanAmtdt1":"매도대금담보대출금액",
            "DpslRestrcAmt":"처분제한금액"
        }
    }

    CSPAQ12300 = {
        "CSPAQ12300OutBlock2" :{
            "RecCnt":"레코드갯수",
            "BrnNm":"지점명",
            "AcntNm":"계좌명",
            "MnyOrdAbleAmt":"현금주문가능금액",
            "MnyoutAbleAmt":"출금가능금액",
            "SeOrdAbleAmt":"거래소금액",
            "KdqOrdAbleAmt":"코스닥금액",
            "HtsOrdAbleAmt":"HTS주문가능금액",
            "MgnRat100pctOrdAbleAmt":"증거금률100퍼센트주문가능금액",
            "BalEvalAmt":"잔고평가금액",
            "PchsAmt":"매입금액",
            "RcvblAmt":"미수금액",
            "PnlRat":"손익율",
            "InvstOrgAmt":"투자원금",
            "InvstPlAmt":"투자손익금액",
            "CrdtPldgOrdAmt":"신용담보주문금액",
            "Dps":"예수금",
            "D1Dps":"D1예수금",
            "D2Dps":"D2예수금",
            "OrdDt":"주문일",
            "MnyMgn":"현금증거금액",
            "SubstMgn":"대용증거금액",
            "SubstAmt":"대용금액",
            "PrdayBuyExecAmt":"전일매수체결금액",
            "PrdaySellExecAmt":"전일매도체결금액",
            "CrdayBuyExecAmt":"금일매수체결금액",
            "CrdaySellExecAmt":"금일매도체결금액",
            "EvalPnlSum":"평가손익합계",
            "DpsastTotamt":"예탁자산총액",
            "Evrprc":"제비용",
            "RuseAmt":"재사용금액",
            "EtclndAmt":"기타대여금액",
            "PrcAdjstAmt":"가정산금액",
            "D1CmsnAmt":"D1수수료",
            "D2CmsnAmt":"D2수수료",
            "D1EvrTax":"D1제세금",
            "D2EvrTax":"D2제세금",
            "D1SettPrergAmt":"D1결제예정금액",
            "D2SettPrergAmt":"D2결제예정금액",
            "PrdayKseMnyMgn":"전일KSE현금증거금",
            "PrdayKseSubstMgn":"전일KSE대용증거금",
            "PrdayKseCrdtMnyMgn":"전일KSE신용현금증거금",
            "PrdayKseCrdtSubstMgn":"전일KSE신용대용증거금",
            "CrdayKseMnyMgn":"금일KSE현금증거금",
            "CrdayKseSubstMgn":"금일KSE대용증거금",
            "CrdayKseCrdtMnyMgn":"금일KSE신용현금증거금",
            "CrdayKseCrdtSubstMgn":"금일KSE신용대용증거금",
            "PrdayKdqMnyMgn":"전일코스닥현금증거금",
            "PrdayKdqSubstMgn":"전일코스닥대용증거금",
            "PrdayKdqCrdtMnyMgn":"전일코스닥신용현금증거금",
            "PrdayKdqCrdtSubstMgn":"전일코스닥신용대용증거금",
            "CrdayKdqMnyMgn":"금일코스닥현금증거금",
            "CrdayKdqSubstMgn":"금일코스닥대용증거금",
            "CrdayKdqCrdtMnyMgn":"금일코스닥신용현금증거금",
            "CrdayKdqCrdtSubstMgn":"금일코스닥신용대용증거금",
            "PrdayFrbrdMnyMgn":"전일프리보드현금증거금",
            "PrdayFrbrdSubstMgn":"전일프리보드대용증거금",
            "CrdayFrbrdMnyMgn":"금일프리보드현금증거금",
            "CrdayFrbrdSubstMgn":"금일프리보드대용증거금",
            "PrdayCrbmkMnyMgn":"전일장외현금증거금",
            "PrdayCrbmkSubstMgn":"전일장외대용증거금",
            "CrdayCrbmkMnyMgn":"금일장외현금증거금",
            "CrdayCrbmkSubstMgn":"금일장외대용증거금",
            "DpspdgQty":"예탁담보수량",
            "BuyAdjstAmtD2":"매수정산금(D+2)",
            "SellAdjstAmtD2":"매도정산금(D+2)",
            "RepayRqrdAmtD1":"변제소요금(D+1)",
            "RepayRqrdAmtD2":"변제소요금(D+2)",
            "LoanAmt":"대출금액"
        },
        "CSPAQ12300OutBlock3":{
            "IsuNo":"종목번호",
            "IsuNm":"종목명",
            "SecBalPtnCode":"유가증권잔고유형코드",
            "SecBalPtnNm":"유가증권잔고유형명",
            "BalQty":"잔고수량",
            "BnsBaseBalQty":"매매기준잔고수량",
            "CrdayBuyExecQty":"금일매수체결수량",
            "CrdaySellExecQty":"금일매도체결수량",
            "SellPrc":"매도가",
            "BuyPrc":"매수가",
            "SellPnlAmt":"매도손익금액",
            "PnlRat":"손익율",
            "NowPrc":"현재가",
            "CrdtAmt":"신용금액",
            "DueDt":"만기일",
            "PrdaySellExecPrc":"전일매도체결가",
            "PrdaySellQty":"전일매도수량",
            "PrdayBuyExecPrc":"전일매수체결가",
            "PrdayBuyQty":"전일매수수량",
            "LoanDt":"대출일",
            "AvrUprc":"평균단가",
            "SellAbleQty":"매도가능수량",
            "SellOrdQty":"매도주문수량",
            "CrdayBuyExecAmt":"금일매수체결금액",
            "CrdaySellExecAmt":"금일매도체결금액",
            "PrdayBuyExecAmt":"전일매수체결금액",
            "PrdaySellExecAmt":"전일매도체결금액",
            "BalEvalAmt":"잔고평가금액",
            "EvalPnl":"평가손익",
            "MnyOrdAbleAmt":"현금주문가능금액",
            "OrdAbleAmt":"주문가능금액",
            "SellUnercQty":"매도미체결수량",
            "SellUnsttQty":"매도미결제수량",
            "BuyUnercQty":"매수미체결수량",
            "BuyUnsttQty":"매수미결제수량",
            "UnsttQty":"미결제수량",
            "UnercQty":"미체결수량",
            "PrdayCprc":"전일종가",
            "PchsAmt":"매입금액",
            "RegMktCode":"등록시장코드",
            "LoanDtlClssCode":"대출상세분류코드",
            "DpspdgLoanQty":"예탁담보대출수량"
        }
    }

    CSPAQ13700 = {
        "CSPAQ13700OutBlock3":{
            "OrdDt":"주문일",
            "MgmtBrnNo":"관리지점번호",
            "OrdMktCode":"주문시장코드",
            "OrdNo":"주문번호",
            "OrgOrdNo":"원주문번호",
            "IsuNo":"종목번호",
            "IsuNm":"종목명",
            "BnsTpCode":"매매구분",
            "BnsTpNm":"매매구분",
            "OrdPtnCode":"주문유형코드",
            "OrdPtnNm":"주문유형명",
            "OrdTrxPtnCode":"주문처리유형코드",
            "OrdTrxPtnNm":"주문처리유형명",
            "MrcTpCode":"정정취소구분",
            "MrcTpNm":"정정취소구분명",
            "MrcQty":"정정취소수량",
            "MrcAbleQty":"정정취소가능수량",
            "OrdQty":"주문수량",
            "OrdPrc":"주문가격",
            "ExecQty":"체결수량",
            "ExecPrc":"체결가",
            "ExecTrxTime":"체결처리시각",
            "LastExecTime":"최종체결시각",
            "OrdprcPtnCode":"호가유형코드",
            "OrdprcPtnNm":"호가유형명",
            "OrdCndiTpCode":"주문조건구분",
            "AllExecQty":"전체체결수량",
            "RegCommdaCode":"통신매체코드",
            "CommdaNm":"통신매체명",
            "MbrNo":"회원번호",
            "RsvOrdYn":"예약주문여부",
            "LoanDt":"대출일",
            "OrdTime":"주문시각",
            "OpDrtnNo":"운용지시번호",
            "OdrrId":"주문자ID",
        }
    }
    CSPAT00600 = {
        "CSPAT00600OutBlock1":{
            "RecCnt":"레코드갯수",
            "AcntNo":"계좌번호",
            "InptPwd":"입력비밀번호",
            "IsuNo":"종목번호",
            "OrdQty":"주문수량",
            "OrdPrc":"주문가",
            "BnsTpCode":"매매구분",
            "OrdprcPtnCode":"호가유형코드",
            "PrgmOrdprcPtnCode":"프로그램호가유형코드",
            "StslAbleYn":"공매도가능여부",
            "StslOrdprcTpCode":"공매도호가구분",
            "CommdaCode":"통신매체코드",
            "MgntrnCode":"신용거래코드",
            "LoanDt":"대출일",
            "MbrNo":"회원번호",
            "OrdCndiTpCode":"주문조건구분",
            "StrtgCode":"전략코드",
            "GrpId":"그룹ID",
            "OrdSeqNo":"주문회차",
            "PtflNo":"포트폴리오번호",
            "BskNo":"바스켓번호",
            "TrchNo":"트렌치번호",
            "ItemNo":"아이템번호",
            "OpDrtnNo":"운용지시번호",
            "LpYn":"유동성공급자여부",
            "CvrgTpCode":"반대매매구분"
        },
        "CSPAT00600OutBlock2":{
            "RecCnt":"레코드갯수",
            "OrdNo":"주문번호",
            "OrdTime":"주문시각",
            "OrdMktCode":"주문시장코드",
            "OrdPtnCode":"주문유형코드",
            "ShtnIsuNo":"단축종목번호",
            "MgempNo":"관리사원번호",
            "OrdAmt":"주문금액",
            "SpareOrdNo":"예비주문번호",
            "CvrgSeqno":"반대매매일련번호",
            "RsvOrdNo":"예약주문번호",
            "SpotOrdQty":"실물주문수량",
            "RuseOrdQty":"재사용주문수량",
            "MnyOrdAmt":"현금주문금액",
            "SubstOrdAmt":"대용주문금액",
            "RuseOrdAmt":"재사용주문금액",
            "AcntNm":"계좌명",
            "IsuNm":"종목명"
        }
    }
    CSPAT00800 = {
        "CSPAT00800OutBlock2":{
            "RecCnt":"레코드갯수",
            "OrdNo":"주문번호",
            "PrntOrdNo":"모주문번호",
            "OrdTime":"주문시각",
            "OrdMktCode":"주문시장코드",
            "OrdPtnCode":"주문유형코드",
            "ShtnIsuNo":"단축종목번호",
            "PrgmOrdprcPtnCode":"프로그램호가유형코드",
            "StslOrdprcTpCode":"공매도호가구분",
            "StslAbleYn":"공매도가능여부",
            "MgntrnCode":"신용거래코드",
            "LoanDt":"대출일",
            "CvrgOrdTp":"반대매매주문구분",
            "LpYn":"유동성공급자여부",
            "MgempNo":"관리사원번호",
            "BnsTpCode":"매매구분",
            "SpareOrdNo":"예비주문번호",
            "CvrgSeqno":"반대매매일련번호",
            "RsvOrdNo":"예약주문번호",
            "AcntNm":"계좌명",
            "IsuNm":"종목명"
        }
    }
        
