

"""
    This module provides KL Divergence related computation


    Author: Juncheng Yang <peter.waynechina@gmail.com> 2018/02

"""

import math


def cal_KL_from_rd_cnt_cdf(p, q, epsilon=0.01):
    """
    p and q are two lists of rd count cdf percentage

    :param p:
    :param q:
    :param epsilon:
    :return:
    """
    # assert len(p) == len(q), "lists have different len {} {}".format(len(p), len(q))
    new_p = p[:]
    new_q = q[:]

    length = max(len(p), len(q))
    if min(len(p), len(q)) == 0:
        print("find one interval with no non-negative rd")
        return -1
    # else:
    #     print("length {} {} {}".format(length, len(p), len(q)))


    if len(p) < length:
        new_p.extend([p[-1]]*(length-len(p)))
    if len(q) < length:
        new_q.extend([q[-1]]*(length-len(q)))

    sum_p = sum(new_p)
    sum_q = sum(new_q)
    new_p = [new_p[i]/sum_p for i in range(len(new_p))]
    new_q = [new_q[i]/sum_q for i in range(len(new_p))]

    assert abs(sum(new_p)-1) < 0.0001 and abs(sum(new_q)-1) < 0.0001, "{} {}".format(sum(new_p), sum(new_q))
    epsilon /= max(len(new_p), len(new_p))
    # print(new_p[:100])
    # print(new_q[:100])
    # print("{} {}".format(len(new_p), len(new_q)))

    # smoothing
    i = 0
    while new_q[i] == 0:
        new_q[i] = epsilon
        i += 1
    if i > 0:
        change_for_rest = epsilon * (i-1) / (len(new_q) - (i-1))
        while i < len(new_q):
            new_q[i] -= change_for_rest
            i += 1

    KL = 0
    for i in range(len(new_p)):
        pi = new_p[i]
        qi = new_q[i]
        if pi == 0:
            continue
        KL += pi * math.log(pi/qi, math.e)
    return KL


def transform_rd_list_to_rd_cnt(rd_list, percentage=True, normalize=False, cdf=True):
    """
    transform a list of reuse distance to a list of reuse distance count

    :param rd_list:
    :param percentage:
    :param normalize:
    :param cdf:
    :return:
    """

    rd_cnt = [0]* (max(rd_list) + 1)
    for rd in rd_list:
        if rd != -1:
            rd_cnt[rd] +=1

    if percentage:
        sum_cnt = sum(rd_cnt)
        for i in range(0, len(rd_cnt)):
            rd_cnt[i] = rd_cnt[i] / sum_cnt

    if cdf:
        for i in range(1, len(rd_cnt)):
            rd_cnt[i] += rd_cnt[i-1]

        if normalize:
            sum_cnt = sum(rd_cnt)
            for i in range(0, len(rd_cnt)):
                rd_cnt[i] = rd_cnt[i] / sum_cnt

    return rd_cnt


def cal_area(p, q):
    """
    p and q are two lists of rd_count cdf

    """

    if len(p) < len(q):
        p.extend([1] * (len(q) - len(p)))
    elif len(p) > len(q):
        q.extend([1] * (len(p) - len(q)))

    return (sum(p) - sum(q))/len(p)
