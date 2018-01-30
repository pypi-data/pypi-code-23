import os

from urllib.request import urlopen
from bs4 import BeautifulSoup


def get_html(url, save=True, save_path='.', save_name='test.html'):
    """获取网页源码

    快速获取网页源码，并下载到本地文件，用于分析结构

    Args:
        url:
        save:
        save_path:
        save_name:

    Returns:

    """

    html_str = urlopen(url).read()
    soup = BeautifulSoup(html_str, "html.parser").prettify()

    if save:
        with open(os.path.join(save_path, save_name), 'w+', encoding="utf-8") as f:
            f.write(soup)

    return soup
