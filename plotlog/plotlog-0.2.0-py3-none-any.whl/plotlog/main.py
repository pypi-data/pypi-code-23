#!/usr/bin/env python
import sys
import argparse
from os.path import isfile

from plotlog.datacut import DataCut
from plotlog.plotgraph import PlotGraph
from plotlog.setting import Setting
from plotlog.selectlog import SelectLog


def main():
    args = arg_parser()

    st = Setting(args.setting)

    if args.copy:
        copy_config(st.default_strings)

    st.configure()

    sl = SelectLog()
    log_file_paths = sl.get_logfile_paths(args, st.setting["put_log_dir"],
                                          st.setting["graph_save_dir"],
                                          st.setting["log_date_type"])
    pg = PlotGraph()

    for log_file_path in log_file_paths:
        data, memo = setup_data_frame(args, st.setting, log_file_path)
        logfile_name = sl.get_fn(log_file_path)

        save_dir = sl.setup_save_dir(logfile_name,
                                     st.setting["log_date_type"],
                                     st.setting["graph_save_dir"])

        for stg in st.graph:
            graph_path = save_dir + "/" + logfile_name + "_" + stg["name"] \
                         + memo + "." + st.setting["graph_extension"]
            pg.plot(log_file_path, graph_path,
                    st.setting, stg, data.x_axis, data.df)
        print("Complete", logfile_name)

        data.dispose()
    st.dispose()


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
