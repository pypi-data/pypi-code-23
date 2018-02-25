import requests
def open_url(url):
	headers = {"user-agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36"}
	res = requests.get(url, headers=headers)

	return res

def url_DTE(res):
	with open("DTE.txt", 'w', encoding="utf-8") as f:
		f.write(str(res.text))
