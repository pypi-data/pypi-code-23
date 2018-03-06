from collections import defaultdict
import json
from offsetbasedgraph import graph, Interval, Translation
from Bio import SeqIO
import re


def create_graph_from_vg_json(file_name):
    f = open(file_name)
    block_sequences = {}

    lines = f.readlines()
    line = json.loads(lines[0])
    nodes = line["node"]
    edges = line["edge"]

    import offsetbasedgraph

    blocks_offset_based_graph = {}
    edges_offset_based_graph = defaultdict(list)
    for node in nodes:
        id = node["id"]
        length = len(node["sequence"])
        #print(id, length)
        blocks_offset_based_graph[id] = length
        block_sequences[id] = node["sequence"].lower()

    for edge in edges:
        edges_offset_based_graph[edge["from"]].append(edge["to"])

    g = graph.Graph(blocks_offset_based_graph, edges_offset_based_graph)

    return g, block_sequences

def create_translation_from_vg_json(json_file_name, g, block_sequences):
    chromosome, chromosome_sequence = map_subgraph_to_chromosome("dm6.fa", g, block_sequences)
    path = find_block_through_graph_matching_sequence(chromosome_sequence, g, block_sequences)

    linear_blocks = {}
    linear_blocks[chromosome] = len(chromosome_sequence)

    linear_graph = graph.Graph(linear_blocks, {})
    last_block = path[-1]
    last_block_length = len(block_sequences[last_block])
    path_interval = Interval(0, last_block_length, path)
    forward_trans = {}
    forward_trans[chromosome] = [path_interval]

    backward_trans = {}
    offset = 0
    for block in path:
        block_length = len(block_sequences[block])
        backward_trans[block] = [Interval(0, block_length, [chromosome], linear_graph)]
        offset += block_length

    trans = Translation(forward_trans, backward_trans, linear_graph)

    return trans


def map_subgraph_to_chromosome(fasta_file, sub_graph, block_sequences):
    """
    Searches the fasta file for the chromosome
    with starting sequence that matches the beginning of the graph.
    Returns the chromosome name.
    """
    start_blocks = g.get_first_blocks()
    assert len(start_blocks) == 1, "len start blocks != 1"
    start_block = start_blocks[0]
    start_sequence = block_sequences[start_block]

    return find_chromosome_with_sequence(fasta_file, start_sequence)



def find_chromosome_with_sequence(fasta_file, sequence):

    fasta_sequences = SeqIO.parse(open(fasta_file),'fasta')
    for fasta in fasta_sequences:
        name, fasta_sequence = fasta.id, str(fasta.seq)
        print(name)
        if re.match(sequence, fasta_sequence, re.I):  # Case insensitive startswith check
            print("found")
            print(name)
            return name, fasta_sequence

    assert False, "Could not find start sequence %s in fasta file" % sequence
    return False


def find_block_through_graph_matching_sequence(sequence, graph, block_sequences):
    """
    Returns a list of blocks (that are connected) matching the sequence
    """
    sequence = sequence.lower()
    first_block = graph.get_first_blocks()[0]
    path = [first_block]
    current_block = first_block
    offset = len(block_sequences[first_block])
    assert sequence.startswith(block_sequences[first_block]), "%s does not start with %s" % (sequence[0:200], block_sequences[first_block])

    while True:
        edges = graph.adj_list[current_block]
        if len(edges) == 0:
            break

        next_block = None
        for potential_next in edges:
            if potential_next not in graph.blocks:
                return path

            if sequence[offset:].startswith(block_sequences[potential_next]):
                next_block = potential_next
                #print("  Match with %s "  % potential_next)
                break
            #else:
            #    print("  Potential edge %s did not match" % potential_next)

        assert next_block is not None
        #print("Next block: %s" % next_block)

        offset += len(block_sequences[next_block])
        path.append(next_block)
        current_block = next_block

    return path



g, block_sequences = create_graph_from_vg_json("x.json")
trans = create_translation_from_vg_json("x.json", g, block_sequences)

print(trans)




