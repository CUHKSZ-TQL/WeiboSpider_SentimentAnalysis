import urllib
# 请求url，刚才生成的那一串api接口
url = "http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=75dbc62e27e14309916153b0c81fb6e5&count=10&expiryDate=0&format=2&newLine=2"
res = urllib.request.urlopen(url=url)
page_source = res.read().decode('utf-8')
page_source.split('\r\n')[:-1]

