# coding=utf-8

import numpy as np
import burst_detection as bd

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def calculate_yaccord_matrix(keyword_count_file, keywords_file):
    top_keywords = []
    top_keywords_dict = {}
    top_keywords_count_dict = {}
    top_keywords_num = 60

    co_occur_array = np.zeros(shape=(top_keywords_num, top_keywords_num))
    count = 0
    for line in open(keyword_count_file):

        keyword = line.split(",")[0]
        top_keywords_count_dict[keyword] = int(line.split(",")[1])
        top_keywords.append(keyword)
        top_keywords_dict[keyword] = count

        count += 1
        if count >= top_keywords_num:
            break

    # load keywords wo count co-occurrence
    for line in open(keywords_file):
        keywords = line.split("|")
        for keyword_x in keywords:
            for keyword_y in keywords:
                if keyword_x == keyword_y:
                    continue
                try:
                    co_occur_array[top_keywords_dict[keyword_x]][top_keywords_dict[keyword_y]] += 1
                except:
                    pass

    co_occur_freq = open("co_occur_freq.csv", "w+")
    for top_keyword in top_keywords:
        co_occur_freq.write(top_keyword+",")

    co_occur_freq.write("\n")

    for line in co_occur_array:
        for ele in line:
            co_occur_freq.write("%d," % ele)
        co_occur_freq.write("\n")

    co_occur_freq.close()

    # calculate yaccord matrix
    yaccord_co_occur_array = np.zeros(shape=(top_keywords_num, top_keywords_num), dtype=np.float64)
    for keyword_x in top_keywords:
        for keyword_y in top_keywords:
            if keyword_x == keyword_y:
                continue

            row = top_keywords_dict[keyword_x]
            col = top_keywords_dict[keyword_y]

            row_count = top_keywords_count_dict[keyword_x]
            col_count = top_keywords_count_dict[keyword_y]

            value = 1.0 * co_occur_array[row][col]/(0.001 + row_count+col_count-co_occur_array[row][col])
            yaccord_co_occur_array[row][col] = value

    yaccord_co_occur_array_freq = open("yaccord_co_occur_array_freq.csv", "w+")
    yaccord_co_occur_array_freq.write(",")
    for idx, top_keyword in enumerate(top_keywords):
        if idx != len(line) - 1:
            yaccord_co_occur_array_freq.write(top_keyword + ",")
        else:
            yaccord_co_occur_array_freq.write(top_keyword)

    yaccord_co_occur_array_freq.write("\n")

    for index, line in enumerate(yaccord_co_occur_array):
        yaccord_co_occur_array_freq.write(top_keywords[index] + ",")
        for idx, ele in enumerate(line):
            ele = ele
            if idx != len(line) - 1:
                yaccord_co_occur_array_freq.write("%f," % ele)
            else:
                yaccord_co_occur_array_freq.write("%f" % ele)
        yaccord_co_occur_array_freq.write("\n")

    yaccord_co_occur_array_freq.close()


if __name__ == '__main__':
    keyword_count_file = "keyword_count.csv"
    keywords_file = "keywords.txt"
    calculate_yaccord_matrix(keyword_count_file, keywords_file)
