from prometheus_client import start_http_server
from prometheus_client.core import _LabelWrapper, Counter


def increment_counters(counters, filter, values):
    for metric in get_formatted_metric_names(filter["metric"]):
        labels = filter.get("labels", None)

        if type(counters[metric]) is not _LabelWrapper:
            counter = counters[metric]
        else:
            counter = counters[metric].labels(**labels)

        if "bytes_tx" in metric:
            counter.inc(values["bytes_tx"])
        elif "bytes_rx" in metric:
            counter.inc(values["bytes_rx"])
        elif "packets_tx" in metric:
            counter.inc(values["packets_tx"])
        elif "packets_rx" in metric:
            counter.inc(values["packets_rx"])


def get_formatted_metric_names(input_name):
    out = []
    for packet_metric in ["packets_rx", "packets_tx", "bytes_rx", "bytes_tx"]:
        out.append(input_name.format(packet_metric=packet_metric))
    return out


def initialize_prometheus_counters(filters):
    metrics = {}
    for filter in filters:
        for packet_metric in ["packets_rx", "packets_tx", "bytes_rx", "bytes_tx"]:
            metric_name = filter["metric"].format(packet_metric=packet_metric)

            if metric_name not in metrics:
                metrics[metric_name] = []

            l = filter.get("labels", {})
            for k, v in l.items():
                if k not in metrics[metric_name]:
                    metrics[metric_name].append(k)
    counters = {}
    for k, v in metrics.items():
        c = Counter(k, 'packets measured on wire', v)
        counters[k] = c
    return counters


def start_server(port):
    start_http_server(port)
