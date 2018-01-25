import random
import subprocess
# for i in range(10):
#     time.sleep(random.randrange(1, 5, 1)*0.1)
#     print("HHHH")

servers = ['au96', 'au93', 'au15', 'au23', 'au53', 'au86', 'au92', 'au90', 'au95', 'au88', 'au28', 'au29', 'au85', 'au25', 'au97', 'au84', 'au64', 'au58', 'au87', 'au65', 'au102', 'au21', 'au22', 'au56', 'au117', 'au113', 'au107', 'au115', 'au116', 'au111']
pings = "5"
for i in servers:
    out = subprocess.check_output(["ping", "-n", "-i", ".2", "-c", pings, i + ".nordvpn.com"])
    print(out)

    # try:
    #     ping_proc = subprocess.Popen(
    #         ["ping", "-i", ".2", "-c", pings, i + ".nordvpn.com"],
    #         stdout=subprocess.PIPE)
    #     # pipe the output of ping to grep.
    #     ping_output = subprocess.check_output(
    #         ("grep", "min/avg/max/"), stdin=ping_proc.stdout)
    #     print(ping_output)
    # except subprocess.CalledProcessError as e:
    #     print(Fore.RED + "Ping Failed to :", i[0], "Skipping it" + Fore.BLUE)
    #     continue
