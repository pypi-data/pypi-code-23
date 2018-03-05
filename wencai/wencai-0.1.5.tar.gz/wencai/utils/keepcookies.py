import os
from selenium import webdriver
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 800))
display.start()



def getHeXinV(url,execute_path=None,ktype='firefox',save=True):
    if ktype == 'firefox':
        if execute_path != None:
            from selenium.webdriver.firefox.options import Options
            firefox_options = Options()
            firefox_options.add_argument('--headless')
            driver = webdriver.Firefox(executable_path=execute_path)
        else:
            driver = webdriver.Firefox()
    elif ktype == 'chrome':
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        if execute_path == None:
            driver = webdriver.Chrome(chrome_options=chrome_options)
            # driver = webdriver.Chrome()
        else:
            driver = webdriver.Chrome(executable_path=execute_path,chrome_options=chrome_options)
            # driver = webdriver.Chrome(executable_path=execute_path)

    elif ktype == 'pj':
        if execute_path == None:
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36"
            )

            driver = webdriver.PhantomJS(desired_capabilities=dcap)
        else:
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
            )
            driver = webdriver.PhantomJS(executable_path=execute_path,desired_capabilities=dcap)

    driver.get(url)
    cookies = driver.get_cookies()
    v = ''
    for i in cookies:
        print(i)
        if 'name' in i.keys():
            if i['name'] == 'v': v = i['value']

    if save == True:
        with open(os.path.dirname(__file__)+'/v.txt','w') as f:
            f.write(v)
    driver.quit()
    return v

if __name__ == '__main__':
    v = getHeXinV("http://www.iwencai.com/traceback/strategy",ktype='firefox')
    print(v)