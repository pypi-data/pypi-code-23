import random, time, requests


def time_sleep(total_time_sleep):
    delay_schedule = list()
    while sum(delay_schedule) < total_time_sleep:
        delay_schedule.append(random.randint(1, 10))
    print("total time sleep", total_time_sleep)
    print(delay_schedule)
    for delay in delay_schedule:
        time.sleep(delay)


def should_stop(url):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    results = requests.get(headers=headers, url=url).json()
    print("results:",results,results['stop'])
    return results['stop']

def time_sleep_with_stop_url(total_time_sleep, url, lower_boundary=1, upper_boundary=10, **options):
    delay_schedule = list()


    while sum(delay_schedule) < total_time_sleep:
        delay_schedule.append(random.randint(lower_boundary, upper_boundary))
    if options.get("debug", False):
        print("total time sleep", total_time_sleep)
        print(delay_schedule)
    for delay in delay_schedule:
        print("should_stop(url)",should_stop(url))
        print("current delay",delay)
        stop_sleep = should_stop(url)
        if stop_sleep:
            print("DETENCION DESDE URL")
            return None
        else:
            print("ESPERO EL TIEMPO TIME-SLEEP")
            time.sleep(delay)
    return delay_schedule
