import requests,json
def send_post(url,data,request_headers):
    results = requests.post(headers=request_headers, data=json.dumps(data), url=url, timeout=None)
    if results.status_code == 200:
        return True,None
    return False,results.reason