#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/23 9:56
# @Author  : chenjw
# @Site    : 
# @File    : report.py
# @Software: PyCharm Community Edition
# @Desc    :  do what

from xlsxwriter.workbook import Workbook
import collections


class Report:
    def __init__(self, name):
        self.name = name
        self.workbook = Workbook(name)

    def close(self):
        if self.workbook is not None:
            self.workbook.close()

    # 添加sheet 表
    def add_sheet(self, sheet_name=None):
        if isinstance(sheet_name, str) and sheet_name != '':
            return self.workbook.add_worksheet(sheet_name)
        else:
            return self.workbook.add_worksheet()

    # 设置行的高度
    def setRow(self, sheet, indexs=None, v=None, dict1=None):
        if isinstance(indexs, list) and isinstance(v, int) and v > 0:
            for index in range(indexs):
                if isinstance(index, int) and index > 0:
                    sheet.set_row(index, v)

        if isinstance(dict1, dict) and len(dict1) > 0:
            for _k, _v in dict1.items():
                if isinstance(_k, int) and isinstance(_v, int) and _k >= 0 and _v > 0:
                    sheet.set_row(_k, _v)

    # 默认的格式化东西
    def default_formate(self, num=1, font_size=14, bold=False, color='black'):
        return self.workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'border': num,
             'font_size': font_size,
             'bold': bold,
             'color': color,
             })

    # 获取 y方向的下标
    def load_sheet_y(self, base, index, size):
        half = int((size + 1) / 2)
        if index >= half:
            return index - half + base
        else:
            return index + base

    # 获取x 方向的下标
    def load_sheet_x(self, base, type, index, size):
        half = int((size + 1) / 2)
        if type == 'key':
            if index >= half:
                return str(chr(ord(base) + 2))
            else:
                return str(chr(ord(base) + 0))
        else:
            if index >= half:
                return str(chr(ord(base) + 3))
            else:
                return str(chr(ord(base) + 1))

    # 拼凑成 一个饼状图需要的数据
    def combine(self, pies, list1, x, y):
        keys = ''
        values = ''
        count = 0
        size = len(list1)
        for index_pie in range(len(pies)):
            pie = pies[index_pie]
            for index_list in range(len(list1)):
                sin = list1[index_list]
                if pie == sin:
                    y_indeed = self.load_sheet_y(y, index_list, size)
                    x_indeed_key = self.load_sheet_x(x, 'key', index_list, size)
                    x_indeed_value = self.load_sheet_x(x, 'value', index_list, size)
                    sin_key = '''$%s$%d''' % (x_indeed_key, y_indeed)
                    sin_value = '''$%s$%d''' % (x_indeed_value, y_indeed)
                    if index_pie == len(pies) - 1:
                        keys += sin_key
                        values += sin_value
                    else:
                        keys += sin_key + ':'
                        values += sin_value + ':'
                    count += 1
                    break
        return keys, values, count

    # 用于填充颜色
    def fillcolor(self, count):
        colors = ['orange', 'blue', 'green', 'cyan', 'yellow', 'pink', 'red', 'gray', 'lime', 'brown', 'magenta',
                  'navy', 'purple', 'silver', 'white', 'black']
        res = []
        for i in range(count):
            i = i % len(colors)
            res.append({'fill': {'color': colors[i]}})
        return res

    # 测试概况
    def summary(self, sheet_name, title, dict1, pies=None, pie_name='default', x_offset=25, y_offset=10):
        if isinstance(dict1, collections.OrderedDict) is False:
            return
        list1 = []
        for k, v in dict1.items():
            list1.append(k)
        summary_sheet = self.add_sheet(sheet_name)
        # 自定义 cell 的大小
        summary_sheet.set_column("A:D", 20)
        row_size = int((len(list1) + 1) / 2)
        self.setRow(summary_sheet, [lambda x: x + 1, [x for x in range(row_size)]])
        # 自定义样式
        title_formate = self.default_formate(font_size=18, bold=True, color='blue')
        common_formate = self.default_formate()
        # 标题
        summary_sheet.merge_range('A1:D1', title, title_formate)
        # 详情
        x = 'A'
        y = 2
        size = len(list1)
        for index in range(len(list1)):
            y_indeed = self.load_sheet_y(y, index, size)
            x_indeed_key = self.load_sheet_x(x, 'key', index, size)
            x_indeed_value = self.load_sheet_x(x, 'value', index, size)
            summary_sheet.write(x_indeed_key + str(y_indeed), list1[index], common_formate)
            summary_sheet.write(x_indeed_value + str(y_indeed), dict1[list1[index]], common_formate)

        current_index = (len(list1) + 1) / 2 + 1

        # 此处为饼状图的分隔符
        if pies is not None:
            keys, values, count = self.combine(pies, list1, x, y)
            if count == 0:
                return
            chart = self.workbook.add_chart({'type': 'pie'})

            serie = {
                'name': pie_name,
                'categories': '''=%s!%s''' % (sheet_name, keys),
                'values': '''=%s!%s''' % (sheet_name, values),
                'points': self.fillcolor(count),
            }
            chart.add_series(serie)
            summary_sheet.insert_chart('A' + str(current_index + 2), chart,
                                       {'x_offset': x_offset, 'y_offset': y_offset})

    def detail(self, sheet_name, dict1, list1, width=20):
        if isinstance(dict1, collections.OrderedDict) is False:
            return
        if isinstance(list1, list) is False:
            return

        detail_sheet = self.add_sheet(sheet_name)
        dst_A = chr(int(ord('A') + len(dict1) - 1))

        # 自定义 cell 的大小
        detail_sheet.set_column('''A:%s''' % (dst_A), width)
        self.setRow(detail_sheet, [lambda x: x + 1, [x for x in range(len(list1) + 2)]])

        # 初始化样式
        table_header_formate = self.default_formate(font_size=16, bold=True)
        common_formate = self.default_formate()

        # 设置表头
        index_x = 0
        for key, value in dict1.items():
            detail_sheet.write('''%s1''' % (chr(index_x + ord('A'))), value, table_header_formate)
            index_x += 1
        # 设置内容
        index_y = 2
        for sin_list in list1:
            if isinstance(sin_list, dict):
                index_x = 0
                for key, _tmp in dict1.items():
                    if key in sin_list.keys():
                        value = sin_list[key]
                    else:
                        value = '-'
                    detail_sheet.write('''%s%d''' % (chr(index_x + ord('A')), index_y), value, common_formate)
                    index_x += 1
                index_y += 1
        # 自动过滤
        detail_sheet.autofilter('''A1:%s%d''' % (dst_A, len(list1) + 1))

if __name__ == '__main__':
    pass