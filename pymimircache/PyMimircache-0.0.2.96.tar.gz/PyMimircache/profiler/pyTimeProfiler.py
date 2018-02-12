# coding=utf-8
"""

    This module is currently used internally to plot multiple IHRC on the same fig,
    the multiple IHRC are usually related, for exmaple,
    IHRC of the same trace with different parameters (algorithms, cache size, cache replacement algorithm parameters)

    This module is named timeProfiler because it should be able to dealing with streaming data in the future,
    and currenly it keeps plotting as the trace is read in, it won't wait until all data ready to plot


    Author: Jason <peter.waynechina@gmail.com>


"""


import time
import matplotlib.ticker as ticker
from queue import Empty
from multiprocessing import Process, Queue
from concurrent.futures import ProcessPoolExecutor, as_completed

import PyMimircache
from PyMimircache.profiler.profilerUtils import get_breakpoints
from PyMimircache.profiler.profilerUtils import draw2d
from PyMimircache.const import cache_name_to_class


def _cal_interval_hit_count_subprocess(
        time_mode,
        time_interval,
        ihc_queue,
        cache_class,
                              cache_size,
                              reader_class,
                              reader_params,
                              cache_params=None):
    """
    subprocess for simulating a cache, this will be used as init func for simulating a cache,
    it reads data from reader and calculates the number of hits and misses

    :param cache_class: the __class__ attribute of cache, this will be used to create cache instance
    :param cache_size:  size of cache
    :param reader_class: the __class__ attribute of reader, this will be used to create local reader instance
    :param reader_params:   parameters for reader, used in creating local reader instance
    :param cache_params:    parameters for cache, used in creating cache
    :return: a tuple of number of hits and number of misses
    """

    if cache_params is None:
        cache_params = {}
    process_reader = reader_class(**reader_params)
    cache = cache_class(cache_size, **cache_params)
    n_hits = 0
    n_misses = 0

    if time_mode == "v":
        for n, req in enumerate(process_reader):
            hit = cache.access(req, )
            if hit:
                n_hits += 1
            else:
                n_misses += 1
            if n !=0 and n % time_interval == 0:
                ihc_queue.put((n_hits, n_misses))
                n_hits = 0
                n_misses = 0

    elif time_mode == "r":
        line = process_reader.read_time_req()
        last_ts = line[0]
        while line:
            t, req = line
            hit = cache.access(req, )
            if hit:
                n_hits += 1
            else:
                n_misses += 1
            if t - last_ts > time_interval:
                ihc_queue.put((n_hits, n_misses))
                n_hits = 0
                n_misses = 0
                last_ts = t
            line = process_reader.read_time_req()

    else:
        raise RuntimeError("unknown time_mode {}".format(time_mode))


    process_reader.close()
    ihc_queue.close()
    # print("size {} \t {}: {}".format(cache_size, n_hits, n_misses))
    return True


def _plot_ihrc(param_list, hr_dict, time_mode, figname, last_one=False):
    """
        This function does the plotting after computation,

    :param param_list:
    :param hr_dict:
    :param time_mode:
    :param figname:
    :param last_one:
    :return:
    """


    length = len(hr_dict[list(hr_dict.keys())[0]])
    if length == 0:
        return

    tick = ticker.FuncFormatter(lambda x, _: '{:.0%}'.format(x / length))

    if last_one:
        # whether this is the last plot since the plotting happens every time_interval
        for i in range(len(param_list) - 1):
            param = param_list[i]
            draw2d(hr_dict[param], label=param, xlabel="{} Time".format("Real" if time_mode == "r" else "Virtual"),
                   ylabel="Hit Ratio", xticks=tick, no_clear=True, no_save=True)
        param = param_list[-1]
        draw2d(hr_dict[param], label=param, xlabel="{} Time".format("Real" if time_mode == "r" else "Virtual"),
                   ylabel="Hit Ratio", xticks=tick, figname=figname)
    else:
        for i in range(len(param_list) - 1):
            param = param_list[i]
            draw2d(hr_dict[param], label=param, xlabel="{} Time".format("Real" if time_mode == "r" else "Virtual"),
                   ylabel="Hit Ratio", no_clear=True, no_save=True)
        param = param_list[-1]
        draw2d(hr_dict[param], label=param, xlabel="{} Time".format("Real" if time_mode == "r" else "Virtual"),
                   ylabel="Hit Ratio", figname=figname)




def plot_IHR(reader,
             time_mode,
             time_interval,
             compare_cache_sizes=(),
             compare_algs=(),
             compare_cache_params=(),
             cache_size=-1, alg=None, cache_param=None, figname="IHRC.png", **kwargs):
    """
    This is the function that does the plotting, it plots interval hit ratio curve of
    different parameters of the same trace on the same plot, and it plots every five seconds

    currrent supported comparisons: cache size, different algorithms, different cache params

    ::NOTE: there is no support for combination of different comparisons, for example,
    you cannot compare cache size and cache replacement algorithm at the same time

    :param reader:
    :param time_mode:
    :param time_interval:
    :param compare_cache_sizes:
    :param compare_algs:
    :param compare_cache_params:
    :param cache_size:
    :param alg:
    :param cache_param:
    :param figname:
    :param kwargs:
    :return:
    """

    assert len(compare_cache_sizes) * len(compare_algs) * len(compare_cache_params) == 0, \
                "You can only specify either compare_cache_sizes or compare_algs or compare_cache_params"

    reader_params = reader.get_params()
    reader_params["open_c_reader"] = False

    if len(compare_cache_sizes):
        assert alg is not None, "please provide alg for profiling"
        pass

    elif len(compare_algs):
        assert cache_size != -1, "Please provide cache size for profiling"

        queue_dict = {compare_algs[i]: Queue() for i in range(len(compare_algs))}
        hr_dict = {compare_algs[i]: [] for i in range(len(compare_algs))}
        processes = {}
        finished = 0

        for n, alg in enumerate(compare_algs):
            cache_class = alg
            if isinstance(alg, str):
                cache_class = cache_name_to_class(alg)
            current_cache_param = None
            if cache_param is not None and len(cache_param)>= n:
                current_cache_param = cache_param[n]

            p = Process(target=_cal_interval_hit_count_subprocess,
                        args=(time_mode, time_interval, queue_dict[alg],
                              cache_class, cache_size, reader.__class__,
                              reader_params, current_cache_param))
            processes[p] = alg
            p.start()


        while finished < len(compare_algs):
            plot_now = False
            for alg, q in queue_dict.items():
                while True:
                    try:
                        hc_mc = queue_dict[alg].get_nowait()
                        hr_dict[alg].append(hc_mc[0] / sum(hc_mc))
                        plot_now = True
                    except Empty:
                        time.sleep(5)
                        break

            if plot_now:
                _plot_ihrc(compare_algs, hr_dict, time_mode, figname)
                time.sleep(5)

            # check whether there are finished computations
            # for future, alg in future_to_alg.items():
            #     if future.done():
            process_to_remove = []
            for p, alg in processes.items():
                if not p.is_alive():
                    finished += 1
                    while True:
                        try:
                            hc_mc = queue_dict[alg].get_nowait()
                            hr_dict[alg].append(hc_mc[0]/sum(hc_mc))
                        except Empty:
                            break
                    queue_dict[alg].close()
                    del queue_dict[alg]
                    process_to_remove.append(p)
                    print("{}/{} {} finished".format(finished, len(compare_algs), alg))
                    print(", ".join(["{:.2f}".format(i) for i in hr_dict[alg]]))

            for p in process_to_remove:
                del processes[p]
            process_to_remove.clear()

        _plot_ihrc(compare_algs, hr_dict, time_mode, figname, last_one=True)



if __name__ == "__main__":
    from PyMimircache.bin.conf import AKAMAI_CSV3
    from PyMimircache.profiler.cHeatmap import CHeatmap
    from PyMimircache.cacheReader.vscsiReader import VscsiReader
    from PyMimircache.cacheReader.csvReader import CsvReader
    from PyMimircache.profiler.profilerUtils import get_breakpoints
    reader = VscsiReader("/home/jason/pycharm/mimircache/data/trace.vscsi")
    # reader = CsvReader("/home/jason/ALL_DATA/akamai3/original/19.28.122.183.anon", init_params=AKAMAI_CSV3)
    reader = CsvReader("/home/jason/ALL_DATA/akamai3/layer/1/185.232.99.68.anon.1", init_params=AKAMAI_CSV3)
    reader = CsvReader("/home/jason/ALL_DATA/akamai3/layer/1/clean0922/oneDayData.sort", init_params=AKAMAI_CSV3)
    # bp = CHeatmap.get_breakpoints(reader, "v", 10000)
    # print(bp)
    # print(get_breakpoints(reader, "v", 10000))

    # plot_IHR(reader, time_mode="v", time_interval=200000, cache_size=800000, compare_algs=("LRU", "ASig3"), figname="19.28.122.183.anon.1_ASig3-800000.png")
    # plot_IHR(reader, time_mode="v", time_interval=200000, cache_size=200000, compare_algs=("LRU", "ASig5"), figname="19.28.122.183.anon.1_ASig5.png")

    if "185.232.99.68.anon" in reader.file_loc:
        plot_IHR(reader, time_mode="v", time_interval=200000, cache_size=200000, compare_algs=("LRU", "Optimal", "ASigOPT"),
                 cache_param=(None, {"reader": reader}, {"reader": reader}), figname="19.28.122.183.anon.1_OPT_size8000.png")

    if "oneDay" in reader.file_loc:
        plot_IHR(reader, time_mode="v", time_interval=2000000, cache_size=200000, compare_algs=("LRU", "Optimal", "ASigOPT"),
                 cache_param=(None, {"reader": reader}, {"reader": reader}), figname="oneDayData_OPT.png")

    # plot_IHR(reader, time_mode="v", time_interval=8000000, cache_size=800000, compare_algs=("LRU", "ASigb"), figname="testOneDayASigb.png")
    # plot_IHR(reader, time_mode="v", time_interval=200000, cache_size=200000, compare_algs=("LRU", "ASig"), figname="19.28.122.183.anon.1_0.98_noDyn.png")
    # plot_IHR(reader, time_mode="v", time_interval=2000, cache_size=8000, compare_algs=("LRU", "ASigb"), figname="t.png") # , figname="IHRC-randomEviction-cacheSizePriority.png")
    # plot_IHR(reader, time_mode="v", time_interval=2000, cache_size=2000, compare_algs=("LRU", "FIFO", "ASig"))