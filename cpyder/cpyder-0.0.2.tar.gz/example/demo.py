# /usr/bin/python
# encoding=utf8
# author=spenly
# mail=i@spenly.com

from cpyder.http_worker import HttpWorker
from cpyder.document_parser import document, select

hw = HttpWorker()
out_cat_file = "data/mybb_cat.csv"


def task(url):
    wf = open(out_cat_file, "w")
    sou_page = hw.get(url)
    # proxy sample
    # hw.set_proxy("spenly.com", "12306")
    doc = document(sou_page)
    cns = doc.xpath("//div[@class='dls']/dl//div[@class='colum']")
    for idx in range(0, len(cns)):
        cat_name = select(cns[idx].xpath("./h3/text()"))
        for sub_cat in cns[idx].xpath(".//p/a"):
            sub_cat_name = select(sub_cat.xpath("./text()"))
            sub_cat_url = select(sub_cat.xpath("./@href"))
            print(" , ".join([cat_name, sub_cat_name, sub_cat_url]))
            wf.write(",".join([cat_name, sub_cat_name, sub_cat_url]) + "\n")
    wf.close()


if __name__ == "__main__":
    task("http://www.mia.com/")
