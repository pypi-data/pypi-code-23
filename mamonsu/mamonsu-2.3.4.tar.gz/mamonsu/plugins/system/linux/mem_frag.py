from mamonsu.plugins.system.plugin import SystemPlugin as Plugin
from operator import add
from math import pow
import re


class Mem_Frag(Plugin):

    def parse_line(self, line):
        line = line.strip()
        parsed_line = re.match("Node\s+(?P<numa_node>\d+).*zone\s+(?P<zone>\w+)\s+(?P<nr_free>.*)", line).groupdict()
        return parsed_line

    def get_per_node_hash(self):
        max_node = 0
        buddyhash = {}
        buddyinfo = open("/proc/buddyinfo").readlines()
        for line in map(self.parse_line, buddyinfo):
                numa_node =  int(line["numa_node"])
                free_fragments = map(int, line["nr_free"].split())
                if numa_node not in buddyhash:
                    buddyhash[numa_node] = free_fragments
                else:
                    buddyhash[numa_node] = map(add, buddyhash[numa_node], free_fragments)
        return buddyhash

    def calc_fraglevel(self):
        combined_hash = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        fraglevel = []
        buddyhash = self.get_per_node_hash()
        for node in buddyhash:
            combined_hash = map(add, buddyhash[node], combined_hash)
        total_free_pages = 0
        for i in range(len(combined_hash)):
            total_free_pages = total_free_pages + int(combined_hash[i]*pow(2, i))

        # fraglevel_for_specific_order = (total_free_pages -sum_free_pages_of_equal_and_senior_orders*100/ total_free_pages)
        # fragmentation is a ratio of how many of available free pages cannot be used for allocations of your order

        for i in range(len(combined_hash)):
            pages_of_senior_and_equal_orders = 0
            for n in range(i, len(combined_hash)):
                pages_of_senior_and_equal_orders = pages_of_senior_and_equal_orders + int(combined_hash[n]*pow(2, n))
            fraglevel_for_specific_order = (float(total_free_pages - pages_of_senior_and_equal_orders)*100)/float(total_free_pages)
            fraglevel.append(fraglevel_for_specific_order)
        total_fraglevel = float(sum(fraglevel))/float(len(fraglevel))
        return total_fraglevel

    def run(self, zbx):
        mem_frag = self.calc_fraglevel()
        zbx.send('system.mem_frag[1]', float(mem_frag))

    def items(self, template):
        return template.item({
            'name': 'System wide memory fragmentation',
            'key': 'system.mem_frag[1]'
        })

    def graphs(self, template):
        items = [{'key': 'system.mem_frag[1]'}]
        graph = {'name': 'System memory fragmentation', 'items': items}
        return template.graph(graph)
