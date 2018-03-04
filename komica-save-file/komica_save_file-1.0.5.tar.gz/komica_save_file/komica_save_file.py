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


def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')


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
        now_time = strftime('%Y-%m-%d_%H-%M', localtime())
        if 'htm' in url:
            folder_name = (title + re.search('\d/(.*?).htm', url)[1] +
                           '_' + now_time)
        elif 'res' in url:
            folder_name = (title + re.search('res=(\d*)', url)[1] +
                           '_' + now_time)
        else:
            folder_name = title + now_time
        download_path = get_download_path() + "\\" + folder_name
        os.makedirs(download_path, exist_ok=True)
        file_thumb = soup.find_all(class_='file-thumb')
        failed = []
        file_num = len(file_thumb)
        for file in file_thumb:
            pic_link = file.get('href')
            pic = urljoin(url, pic_link)
            file_name = re.search('src\/(\d*\..*)', pic_link)[1]
            try:
                res = requests.get(pic, stream=True)
                with open(download_path + '\\' + file_name, 'wb') as output:
                    shutil.copyfileobj(res.raw, output)
                del res
            except Exception as e:
                failed.append(pic + '\n')
            finally:
                sleep(0.5)
    print('%d of %d files successfully downloaded in %.2fs' %
          (file_num - len(failed), file_num, float(time() - start)))
    if failed:
        with open(download_path + '\\failed_files.txt', 'w+') as f:
            for i in failed:
                f.write(i)


if __name__ == '__main__':
    save_file()
