import quandl

quandl.ApiConfig.api_key = 'usZHh_yAsopuc9bforqC'
data = quandl.get('BCHARTS/BITFLYERUSD', start_date='2019-03-07', end_date='2019-03-07')

print(data)
