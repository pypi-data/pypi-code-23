import requests
from time import localtime, strftime, sleep, time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import shutil
import os


pat = re.compile(r'^(?:http|ftp)s?://'  # http:// or https://
                 r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  #domain...
                 r'localhost|'  # localhost...
                 r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                 r'(?::\d+)?'  # optional port
                 r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def save_file():
    print('Please enter url')
    while True:
        url = input()
        if re.match(pat, url):
            break
        else:
            print('Please enter valid url')
    start = time()
    r = requests.get(url)
    r.encoding = 'utf-8'
    if not r.ok:
        return(str(r.status_code) + 'Error')
    else:
        soup = BeautifulSoup(r.text)
        title = soup.find('h1').text + '_'
        if 'htm' in url:
            folder_name = (title + re.search('\d/(.*?).htm', url)[1] + '_' +
                           strftime('%Y-%m-%d_%H-%M', localtime()))
        elif 'res' in url:
            folder_name = (title + re.search('res=(\d*)', url)[1] + '_' +
                           strftime('%Y-%m-%d_%H-%M', localtime()))
        else:
            folder_name = title + strftime('%Y-%m-%d_%H-%M', localtime())
        os.makedirs("./" + folder_name, exist_ok=True)
        file_text = soup.find_all(class_='file-text')
        for file in file_text:
            pic_link = file.a.get('href')
            pic = urljoin(url, pic_link)
            name = file.a.text
            res = requests.get(pic, stream=True)
            with open('./' + folder_name + '/' + name, 'wb') as output:
                shutil.copyfileobj(res.raw, output)
            del res
            sleep(0.5)
    print('Download finished in %.2fs' % float(time() - start))


if __name__ == '__main__':
    save_file()
