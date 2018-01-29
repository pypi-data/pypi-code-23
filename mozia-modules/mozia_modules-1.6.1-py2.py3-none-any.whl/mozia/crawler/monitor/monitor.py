# -*- coding: UTF-8 -*-
import re
from modules.scheduler import task_scheduler
from mozia.crawler.repository import dao
from mozia.crawler.proxy import crawl_product


class ProductMonitor:
    def __init__(self):
        self.name = ''
        if not dao.task.get_monitor_task_length() > 0:
            dao.task.create_monitor_tasks()

    def start(self):
        task = dao.task.get_monitor_task()
        while task:
            task['is_monitor'] = True
            task['language_id'] = 1
            source = crawl_product(task)
            self.check_product(task, source)
            task = dao.task.get_monitor_task()

    @staticmethod
    def check_product_sold_out(task, source_product):
        status = source_product.get('status')
        # 商品已售罄
        if 100 == status or 101 == status:
            dao.monitor.set_platform_product_status(task['product_id'], 0)
            return False

        sizes = source_product['sizes']
        if not sizes or len(sizes) == 0:
            dao.monitor.set_platform_product_status(task['product_id'], 0)
            return False

        return True

    def check_product(self, task, source_product):
        # print(task, source)
        if not self.check_product_sold_out(task, source_product):
            print('product sold out,', task)
            dao.monitor.update_monitored_time(task, 0)
            return
        status = 1 if self.check_product_sizes(task, source_product) else 0
        # 下架商品
        if 0 == status:
            dao.monitor.set_platform_product_status(task['product_id'], 0)

        # 更新监控时间
        dao.monitor.update_monitored_time(task, status)

    @staticmethod
    def get_sizes_mapped(source):
        sizes_mapped = {}
        for size in source['sizes']:
            sizes_mapped[size['size']] = size
            if '均码' == size['size']:
                sizes_mapped['OS'] = size
        return sizes_mapped

    @staticmethod
    def get_size_key(size):
        pattern = re.compile('^(\w+|\d+)\[.*\]$')
        match = pattern.match(size)
        if match:
            return match.group(1)

        if size.upper() == 'ONE SIZE':
            return '均码'

        if size.upper() == 'ONESIZE':
            return '均码'

        return size

    def check_product_sizes(self, task, source):
        platform_product = dao.monitor.get_platform_product(task['product_id'])
        if not platform_product:
            print("product no found:", task)
            return True

        sizes_mapped = self.get_sizes_mapped(source)
        product_id = task['product_id']
        source_type = task['source_type']

        sizes_no_found = 0
        for sku in platform_product['skus']:
            size_key = self.get_size_key(sku['size'])
            print('[%s:%s]check product size:%s => %s' % (product_id, source_type, size_key, sku['size']))
            if not sizes_mapped.get(size_key):
                dao.monitor.set_platform_product_sizes_status(product_id, sku['size'], 'OFF')
                sizes_no_found += 1
            else:
                quantity = sizes_mapped[size_key].get('quantity')
                if quantity:
                    print("[%s]set size quantity:%s")
                    dao.monitor.set_platform_product_size_quantity(product_id, sku['size'], quantity)

        return len(platform_product['skus']) > sizes_no_found


if __name__ == "__main__":
    task_scheduler.connect()
    monitor = ProductMonitor()
    assert ('40' == monitor.get_size_key('40[IT]'))
    assert ('40' == monitor.get_size_key('40'))
    assert ('均码' == monitor.get_size_key('One Size'))
    assert ('均码' == monitor.get_size_key('OneSize'))
    assert ('均码' == monitor.get_size_key('One size'))
    assert ('44' == monitor.get_size_key('44[IT/FR]'))
    assert ('XL' == monitor.get_size_key('XL[IT]'))
