#!python

from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin
import argparse
import asyncio
import json
import os
import ssl
import statistics
import sys

import aiohttp
import certifi
import yaml

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


@dataclass
class Context:
    times: list
    failures: list
    status: int = field(default=200)


@dataclass
class Test:
    name: str
    description: str
    version: str
    url: str
    status: int = field(default=200)
    method: str = field(default="get")
    headers: dict = field(default=dict)
    json: dict = field(default=None)
    warmup: int = field(default=0)
    iterations: int = field(default=3)
    timeout: int = field(default=5*60) # This is the aiohttp default anyway.


@dataclass
class Result:
    timeouts: int
    failures: list
    name: str = field(default="")
    description: str = field(default="")
    version: str = field(default="")
    mean: float = field(default=0.0)
    median: float = field(default=0.0)
    stdev: float = field(default=0.0)


async def on_request_start(session, trace, params):
    trace.start = session.loop.time()


async def on_request_end(session, trace, params):
    elapsed = session.loop.time() - trace.start
    if params.response.status == trace.trace_request_ctx.status:
        trace.trace_request_ctx.times.append(elapsed)
    else:
        trace.trace_request_ctx.failures.append(params.response.status)


async def do_request(method, url, headers=None, data=None, context=None):
    response = await method(url, headers=headers, data=data, ssl=SSL_CONTEXT,
                            trace_request_ctx=context)
    return response.status


async def run_one_test(loop, test):
    tc = aiohttp.TraceConfig()
    tc.on_request_start.append(on_request_start)
    tc.on_request_end.append(on_request_end)

    timeouts = 0
    times = []
    failures = []

    async with aiohttp.ClientSession(
            loop=loop, trace_configs=[tc],
            read_timeout=test.timeout) as session:
        method = getattr(session, test.method)
        context = Context(times, failures)

        for _ in range(test.warmup + test.iterations):
            try:
                await do_request(method, test.url, headers=test.headers,
                                 data=test.json, context=context)
            except asyncio.TimeoutError:
                timeouts += 1

    result = Result(timeouts, failures)
    num_times = len(times)

    # Need at least two runs to calculate any of this.
    if num_times >= 2:
        runs = times[slice(test.warmup, num_times)]
        result.mean = statistics.mean(runs)
        result.median = statistics.median(runs)
        result.stdev = statistics.stdev(runs)
    elif num_times == 1:
        # If we only had one succeed, just use it directly.
        result.mean = times[0]
        result.median = times[0]
        result.stdev = 0

    return result


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config", dest="config_path",
                        help="Path to the configuraton file",
                        required=True)
    parser.add_argument("-o", "--output", dest="output_path",
                        # Technically the default here is None,
                        # but we later interpret None to be sys.stdout
                        help="Path to the output file (default: sys.stdout)")
    parser.add_argument(
        "-i", "--id", dest="run_id",
        default=datetime.strftime(datetime.now(), "%Y%m%d%H%M%S%f"),
        help="The run ID, likely a branch checksum")

    values = parser.parse_args()

    return values.config_path, values.output_path, values.run_id

def get_tests(path):
    with open(path, "r") as config_file:
        config = yaml.load(config_file.read())

    try:
        # Right now root is the only default, applied to test urls.
        default = config.pop("default")
        if "root" in default:
            root = default.pop("root")
    except KeyError:
        default = {}
        root = None

    tests = []
    for test_name, values in config.items():
        # If there's a configured root url, join it up, otherwise
        # we'll assume the url is fully formed.
        if root is not None:
            values["url"] = urljoin(root, values["url"])

        test = dict(default)
        test["name"] = test_name

        # Fill in templated header values from environment variables
        if "headers" in values:
            for key, value in values["headers"].items():
                values["headers"][key] = value.format(**os.environ)

        # If we get json in here, dump it to a real JSON-encoded string
        # now rather than making aiohttp do it.
        if "json" in values:
            values["json"] = json.dumps(values["json"])

        test.update(values)

        yield Test(**test)


def run_tests(loop, tests):
    for test in tests:
        result = loop.run_until_complete(run_one_test(loop, test))
        result.name = test.name
        result.description = test.description
        result.version = test.version
        yield result


def write_output(results, output_path, run_id):
    report = {"results": [], "id": run_id}
    for result in results:
        report["results"].append(result.__dict__)

    output = json.dumps(report)

    if output_path is None:
        sys.stdout.write(output)
    else:
        with open(output_path, "w") as out:
            out.write(output)


def main():
    config_path, output_path, run_id = get_args()

    loop = asyncio.get_event_loop()

    tests = get_tests(config_path)
    results = run_tests(loop, tests)
    write_output(results, output_path, run_id)

    loop.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
