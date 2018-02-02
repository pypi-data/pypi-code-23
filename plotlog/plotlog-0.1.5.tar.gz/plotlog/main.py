#!/usr/bin/env python3
import os
import re
import sys
import copy
import argparse
from glob import glob
from os.path import splitext, basename, isfile, isdir

from src.datacut import DataCut
from src.plotgraph import PlotGraph
from src.setting import Setting


def main():
    args = arg_parser()

    st = Setting(args.setting)

    if args.copy:
        copy_config(st.default_strings)

    st.configure()

    log_file_paths = get_log_file_paths(args, st.setting)
    pg = PlotGraph()

    for log_file_path in log_file_paths:
        data, memo = setup_data_frame(args, st.setting, log_file_path)
        log_file_name = splitext(basename(log_file_path))[0]

        if is_fn_in_date(log_file_name, st.setting["log_date_type"]) is None:
            save_dir = st.setting["graph_save_dir"] + "other/" + log_file_name
            if not isdir(save_dir):
                os.makedirs(save_dir)
        else:
            date_time, date = get_date(log_file_path,
                                       st.setting["log_date_type"])
            save_dir = st.setting["graph_save_dir"] + date + "/" + date_time
            if not isdir(save_dir):
                os.makedirs(save_dir)

        for stg in st.graph:
            graph_path = save_dir + "/" + log_file_name + "_" + stg["name"] \
                         + memo + "." + st.setting["graph_extension"]
            pg.plot(log_file_path, graph_path,
                    st.setting, stg, data.x_axis, data.df)
        print("Complete", log_file_name)

        data.dispose()
    st.dispose()


def get_log_file_paths(args, st):
    paths = []
    if args.input:
        paths = copy.copy(args.input)
    elif args.all:
        paths = glob(st["put_log_dir"]+"*")
    elif args.after:
        for path in glob(st["put_log_dir"] + "*"):
            fn = splitext(basename(path))[0]
            if fn >= args.after[0] and is_fn_in_date(fn, st["log_date_type"]):
                paths.append(path)
    elif args.select:
        for date in args.select:
            path = st["put_log_dir"] + date + "." + st["log_extension"]
            paths.append(path)
    elif args.new:
        for path in glob(st["put_log_dir"] + "*"):
            date_time, date = get_date(path, st["log_date_type"])
            if not isdir(st["graph_save_dir"] + date + "/" + date_time):
                paths.append(path)

    for path in paths:
        if not isfile(path):
            print(path, "is not exits.")
            paths.remove(path)
    if len(paths) == 0:
        print("There is no target log file.")
        sys.exit()
    return paths


def setup_data_frame(args, st, path):
    data = DataCut(path)
    data.import_file(st["header_row"], st["log_separate_char"])
    data.set_x_axis(st["xaxis_col"])
    memo = ""
    if args.noshift:
        memo += "_noshift"
    else:
        data.shift(st["shift_trig_col"], st["shift_trig_val"])
    if args.slice:
        data.slice(args.slice)
        st["xlim"] = [float(args.slice[0]), float(args.slice[1])]
        memo += "_slice_" + args.slice[0] + "_" + args.slice[1]
    return data, memo


def get_date(path, f_type):
    date_time = splitext(basename(path))[0]
    date = date_time[0:6] if f_type == 0 or f_type == 1 else date_time[0:8]
    return date_time, date


def is_fn_in_date(s, f_type):
    if f_type == 0:
        return re.search("[%s]" % s, "[0-9]{2}[0-1][0-9][0-3][0-9]"
                                     "[0-2][0-9][0-5][0-9][0-5][0-9]")
    elif f_type == 1:
        return re.search("[%s]" % s, "[0-9]{2}[0-1][0-9][0-3][0-9]"
                                     "[0-2][0-9][0-5][0-9]")
    elif f_type == 2:
        return re.search("[%s]" % s, "[0-9]{4}[0-1][0-9][0-3][0-9]"
                                     "[0-2][0-9][0-5][0-9][0-5][0-9]")
    elif f_type == 3:
        return re.search("[%s]" % s, "[0-9]{4}[0-1][0-9][0-3][0-9]"
                                     "[0-2][0-9][0-5][0-9]")
    else:
        print("error: log_date_type is 0 or 1 or 2 or 3")
        sys.exit()


def copy_config(string):
    if not isfile("user.yml"):
        with open('user.yml', 'w') as f:
            f.writelines(string)
        sys.exit()
    i = 1
    while True:
        path = "user-"+str(i)+".yml"
        if not isfile(path):
            with open(path, 'w') as f:
                f.writelines(string)
            sys.exit()
        i += 1


def arg_parser():
    parser = argparse.ArgumentParser(
        description='Plot graph for many log file that is managed by DATE')
    group1 = parser.add_mutually_exclusive_group()
    parser.add_argument("--setting",
                        help="select setting file (default:'user.yml')",
                        action="store",
                        nargs=1,
                        default="user.yml",
                        metavar="SETTING_FILE_PATH")
    parser.add_argument("--copy",
                        help="copy original setting file",
                        action="store_true")
    group1.add_argument("--new",
                        help="DEFAULT: output graphs that has not been output yet",
                        action="store_true",
                        default=True)
    group1.add_argument("--all",
                        help="output graphs for all data",
                        action="store_true")
    group1.add_argument("--after",
                        help="output graphs after the selected DATE(yyyymmddhhmm)",
                        action="store",
                        nargs=1,
                        metavar="DATE")
    group1.add_argument("--select",
                        help="output graphs only selected DATEs",
                        action="store",
                        nargs="+",
                        metavar="DATE")
    group1.add_argument("--input",
                        help="output graphs for selected log file",
                        action="store",
                        nargs="+",
                        metavar="LOG_FILE_PATH")
    parser.add_argument("--slice",
                        help="sliced data by begin and end x-axis value",
                        action="store",
                        nargs=2,
                        metavar=("BEGIN", "END"))
    parser.add_argument("--noshift",
                        help="don't shift plot start time and x-axis",
                        action="store_true")
    return parser.parse_args()


if __name__ == '__main__':
    main()
