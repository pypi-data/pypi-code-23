# -*- coding: UTF-8 -*-
# 显示函数执行时间
import sys
from datetime import datetime
from json import loads, dumps
from random import random


def exec_time(func):
    def inner(*args, **kwargs):
        begin = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        inter = end - begin
        print('Execute time: {0}.{1}s'.format(
            inter.seconds,
            inter.microseconds
        ))
        return result

    return inner


@exec_time
def insert_sort(array):
    # 插入排序：直接插入排序-稳定
    for i in range(len(array)):
        for j in range(i):
            if array[i] < array[j]:
                array.insert(j, array.pop(i))
                break
    return array


@exec_time
def shell_sort(array):
    # 插入排序：希尔排序-不稳定
    gap = len(array)
    while gap > 1:
        gap = gap // 2
        for i in range(gap, len(array)):
            for j in range(i % gap, i, gap):
                if array[i] < array[j]:
                    array[i], array[j] = array[j], array[i]
    return array


@exec_time
def select_sort(array):
    # 选择排序：简单选择排序-不稳定
    for i in range(len(array)):
        x = i  # min index
        for j in range(i, len(array)):
            if array[j] < array[x]:
                x = j
        array[i], array[x] = array[x], array[i]
    return array


@exec_time
def heap_sort(array):
    # 选择排序：堆排序-不稳定
    def heap_adjust(parent):
        child = 2 * parent + 1  # left child
        while child < len(heap):
            if child + 1 < len(heap):
                if heap[child + 1] > heap[child]:
                    child += 1  # right child
            if heap[parent] >= heap[child]:
                break
            heap[parent], heap[child] = \
                heap[child], heap[parent]
            parent, child = child, 2 * child + 1

    heap, array = array.copy(), []
    for i in range(len(heap) // 2, -1, -1):
        heap_adjust(i)
    while len(heap) != 0:
        heap[0], heap[-1] = heap[-1], heap[0]
        array.insert(0, heap.pop())
        heap_adjust(0)
    return array


@exec_time
def bubble_sort(array):
    # 交换排序：冒泡排序-稳定
    for i in range(len(array)):
        for j in range(i, len(array)):
            if array[i] > array[j]:
                array[i], array[j] = array[j], array[i]
    return array


@exec_time
def quick_sort(array):
    # 交换排序：快速排序-不稳定
    def recursive(begin, end):
        if begin > end:
            return
        left, right = begin, end
        pivot = array[left]
        while left < right:
            while left < right and array[right] > pivot:
                right -= 1
            while left < right and array[left] <= pivot:
                left += 1
            array[left], array[right] = array[right], array[left]
        array[left], array[begin] = pivot, array[left]
        recursive(begin, left - 1)
        recursive(right + 1, end)

    recursive(0, len(array) - 1)
    return array


@exec_time
def merge_sort(array):
    # 归并排序-稳定
    def merge_arr(arr_l, arr_r):
        _array = []
        while len(arr_l) and len(arr_r):
            if arr_l[0] <= arr_r[0]:
                _array.append(arr_l.pop(0))
            elif arr_l[0] > arr_r[0]:
                _array.append(arr_r.pop(0))
        if len(arr_l) != 0:
            _array += arr_l
        elif len(arr_r) != 0:
            _array += arr_r
        return _array

    def recursive(_array):
        if len(_array) == 1:
            return _array
        mid = len(_array) // 2
        arr_l = recursive(_array[:mid])
        arr_r = recursive(_array[mid:])
        return merge_arr(arr_l, arr_r)

    return recursive(array)


@exec_time
def radix_sort(array):
    # 基数排序-稳定
    bucket, digit = [[]], 0
    while len(bucket[0]) != len(array):
        bucket = [[], [], [], [], [], [], [], [], [], []]
        for i in range(len(array)):
            num = (array[i] // 10 ** digit) % 10
            bucket[num].append(array[i])
        array.clear()
        for i in range(len(bucket)):
            array += bucket[i]
        digit += 1
    return array


# 生成随机数文件
def dump_random_array(file='numbers.json', size=10 ** 4):
    fo = open(file, 'w', 1024)
    random_list = list()
    for i in range(size):
        random_list.append(int(random() * 10 ** 10))
    fo.write(dumps(random_list))
    fo.close()


# 加载随机数列表
def load_random_array(file='numbers.json'):
    fo = open(file, 'r', 1024)
    try:
        random_list = fo.read()
    finally:
        fo.close()
    return loads(random_list)


if __name__ == '__main__':
    # 如果数据量特别大, 采用分治算法的快速排序和归并排序, 可能会出现递归层次超出限制的错误.
    # 解决办法：导入 sys 模块（import sys）, 设置最大递归次数（sys.setrecursionlimit(10 ** 8)）.
    sys.setrecursionlimit(10 ** 8)
    # dump_random_array()
    arr = load_random_array()
    # print('插入排序：直接插入排序', insert_sort(arr) == sorted(arr))  # Execute time: 2.865568s
    # print('插入排序：希尔排序', shell_sort(arr) == sorted(arr))  # Execute time: 11.645593s
    # print('选择排序：简单选择排序', select_sort(arr) == sorted(arr))  # Execute time: 5.892854s
    print('选择排序：堆排序', heap_sort(arr) == sorted(arr))  # Execute time: 0.139123s
    # print('交换排序：冒泡排序', bubble_sort(arr) == sorted(arr))  # Execute time: 8.794577s
    # print('交换排序：快速排序', quick_sort(arr) == sorted(arr))  # Execute time: 0.66999s
    print('归并排序', merge_sort(arr) == sorted(arr))  # Execute time: 0.118023s
    # print('基数排序', radix_sort(arr) == sorted(arr))  # Execute time: 0.65139s
    quit()
