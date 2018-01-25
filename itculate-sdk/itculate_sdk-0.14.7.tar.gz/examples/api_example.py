import pprint
from unix_dates import UnixDate

__author__ = 'ran'

from collections import defaultdict
from itculate_sdk.connection import ApiConnection


# server_url = "http://localhost:5000/api/v1"
server_url = None

api_key = "fwvU0f5H1eLmcKyqcauXE4nEDhPZQzWT"
api_secret = "KgelEfRDLTESk2olOnH2CJq_g2zEYrIBlYTuNzktd6HjmzCFu7_79ygQdgjh-h1D"

connection = ApiConnection(api_key=api_key, api_secret=api_secret, server_url=server_url)
# url = "tenants/3nvQ3n6nk1j1X6nji34PB/vertices?type=AWS_Instance&name_pattern=.*cassa.*&limit=200"
# url = "tenants/3nvQ3n6nk1j1X6nji34PB/vertices?type=AWS_Instance&expand=analytics_timeseries_statistics&limit=1500"
url = "tenants/3nvQ3n6nk1j1X6nji34PB/vertices?type=AWS_Auto_Scaling_Group&expand=analytics_timeseries_statistics&limit=1500"
vertices = connection.get(url)
# vertices = connection.get("tenants/3nvQ3n6nk1j1X6nji34PB/vertices?type=AWS_Instance&name_pattern=.*cassa.*&limit=200")

now = UnixDate.now()
total_idle_monthly_price = 0
count_idle = 0
result = []
result2 = []
for vertex in vertices:
    tags = vertex.get("tags", {})
    # instance_id = vertex["instance-id"]
    instance_type = vertex["launch-configuration"]["instance-type"]  # vertex["instance-type"]
    name = vertex["_name"]
    region = vertex["region"]
    cluster = tags.get("Cluster")
    service = tags.get("Service")
    monthly_price = vertex["estimated-cost"]
    instance_count = len(vertex["instances"])
    min_size = vertex["min-size"]
    max_size = vertex["max-size"]

    launch_time = vertex.get("create-time")
    statistics = vertex.get("_links", {}).get("analytics_timeseries_statistics").get("statistics", {})
    if not statistics:
        continue

    days_up = (now - launch_time) / (60 * 60 * 24)

    # days_up = 10

    network_max = statistics.get("network", {}).get("max")
    network_95 = statistics.get("network", {}).get("95%")
    cpu_max = statistics.get("cpu-utilization", {}).get("max")
    cpu_95 = statistics.get("cpu-utilization", {}).get("95%")
    ebs_iops_max = statistics.get("ebs-total-iops", {}).get("max")
    ebs_iops_95 = statistics.get("ebs-total-iops", {}).get("95%")

    ephemeral_iops_max = statistics.get("ephemeral-disk-total-iops", {}).get("max")
    ephemeral_iops_95 = statistics.get("ephemeral-disk-total-iops", {}).get("95%")

    if cpu_95 and network_95 and cpu_max < 0.13 and network_max < 10 and days_up > 7:
    # if True:
        total_idle_monthly_price += monthly_price
        count_idle += 1
        text2 = ""
        # if service:
        #     text += "Service: " + service + " "
        # if cluster:
        #     text += "Cluster: " + cluster + " "

        text = "Service {}  " \
               "Region {} " \
               "ASG {} " \
               "cpu_95 {}%   " \
               "cpu_max {}%   " \
               "EBS iops_95 {}%   " \
               "EBS iops_max {}%   " \
               "ephemeral iops_95 {}%   " \
               "ephemeral iops_max {}%   " \
               "network_95 {}MB     " \
               "network_max {}MB  " \
               "min size {}  " \
               "max size {}  " \
               "Estimated Monthly price ${}  " \
               "Days {} " \
               "Instance Type {} " \
               "Instance count {} " \
               "".format(region,
                         service,
                         name,
                         round(100 * cpu_95, 2),
                         round(100 * cpu_max, 2),
                         round(ebs_iops_95, 2),
                         round(ebs_iops_max, 2),
                         round(ephemeral_iops_95, 2) if ephemeral_iops_95 else "NaN",
                         round(ephemeral_iops_max, 2) if ephemeral_iops_max else "NaN",
                         round(network_95, 2),
                         min_size,
                         max_size,
                         round(network_max, 2),
                         round(monthly_price, 1),
                         round(days_up, 1),
                         instance_type,
                         instance_count)

        text2 = "{},{},{},{},{},{},{},{},{},{},{},{},{},${},{},{},{} ".format(
            service,
            region,
            name,
            round(100 * cpu_95, 2),
            round(100 * cpu_max, 2),
            round(ebs_iops_95, 2),
            round(ebs_iops_max, 2),
            round(ephemeral_iops_95, 2) if ephemeral_iops_95 else "NaN",
            round(ephemeral_iops_max, 2) if ephemeral_iops_max else "NaN",
            round(network_95, 2),
            round(network_max, 2),
            min_size,
            max_size,
            round(monthly_price, 1),
            round(days_up, 1),
            instance_type,
            instance_count)

        result.append(text)
        result2.append(text2)
#
# for r in sorted(result):
#     print r

print "Service,Region,Scaling Group,CPU_95,CPU_max,EBS IOps_95,EBS IOps_max,Ephemeral IOps_95,Ephemeral IOps_max," \
      "Network_95,Network_max,Min-Size,Max-Size,Estimated Monthly Price,Day,Instance Type,Instance count"
for r in sorted(result2):
    print r

print "Instances {}".format(count_idle)
print "Monthly total saving ${}".format(int(total_idle_monthly_price))
print "Yearly total saving ${}".format(int(total_idle_monthly_price * 12))

