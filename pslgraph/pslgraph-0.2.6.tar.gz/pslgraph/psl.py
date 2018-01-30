import logging
import os
import subprocess

import psutil

from .constants import *
from .networkx import Graph
from .util import get_logger, write_tsv

DATA_FILE_SUB = '{data_dir}'
DEFAULT_MEMORY_PERCENT = 0.75

def writePSLData(graph, base_path = DEFAULT_DATA_DIR, include_all_edges = False):
    """
    Decompose the graph into data for a PSL link prediction model.
    Every unobserved link (where a link exists, but has the property: 'observed': False) is a target.
    """
    logger = get_logger(__name__)
    logger.debug("Writing PSL data into '%s'", base_path)

    os.makedirs(base_path, exist_ok = True)

    _write_predicate_graph(graph, os.path.join(base_path, GRAPH1_PREDICATE_FILENAME), NODE_MODIFIER_SOURCE)
    _write_predicate_graph(graph, os.path.join(base_path, GRAPH2_PREDICATE_FILENAME), NODE_MODIFIER_TARGET)
    _write_predicate_edge(graph, os.path.join(base_path, EDGE1_PREDICATE_FILENAME), NODE_MODIFIER_SOURCE)
    _write_predicate_edge(graph, os.path.join(base_path, EDGE2_PREDICATE_FILENAME), NODE_MODIFIER_TARGET)
    _write_predicate_link_prior(graph, os.path.join(base_path, LINK_PRIOR_PREDICATE_FILENAME))
    _write_predicate_link_observed(graph, os.path.join(base_path, LINK_PREDICATE_OBS_FILENAME))

    if (include_all_edges):
        _write_predicate_link_target_all(graph, os.path.join(base_path, LINK_PREDICATE_TARGET_FILENAME))
    else:
        _write_predicate_link_target(graph, os.path.join(base_path, LINK_PREDICATE_TARGET_FILENAME))

    _write_predicate_block(graph, os.path.join(base_path, BLOCK_PREDICATE_FILENAME))

def runModel(model_name, data_path = DEFAULT_DATA_DIR):
    logger = get_logger(__name__)
    logger.debug("Running PSL model, %s, with data from '%s'", model_name, data_path)

    # TODO(eriq): We need a directory to run things in.
    run_dir = data_path

    model_path = os.path.join(PSL_CLI_DIR, "%s.psl" % (model_name))
    data_file_path = _generate_data_file(data_path, model_name)
    values = _run_psl(model_path, data_file_path, run_dir)

    return values

# predicate_values should be {[atom arg, ...]: link value, ...}
def buildOutputGraph(predicate_values, in_graph):
    graph = Graph()

    for link in predicate_values:
        if (len(link) != 2):
            raise ValueError("Expecting links of length 2, got %s: (%s)." % (len(link), link))

        # TODO(eriq): Double check int/string consistency
        # source_id, target_id = str(link[0]), str(link[1])
        source_id, target_id = link[0], link[1]

        graph.add_node(source_id, **(in_graph.node[source_id]))
        graph.add_node(target_id, **(in_graph.node[target_id]))

        attributes = {
            WEIGHT_KEY: predicate_values[link],
            EDGE_TYPE_KEY: EDGE_TYPE_LINK,
            INFERRED_KEY: True
        }
        graph.add_edge(source_id, target_id, **attributes)

    return graph

def _generate_data_file(data_path, model_name):
    template_path = os.path.join(PSL_CLI_DIR, "%s_template.data" % (model_name))
    out_path = os.path.join(data_path, 'psl.data')

    with open(out_path, 'w') as outFile:
        with open(template_path, 'r') as inFile:
            for line in inFile:
                outFile.write(line.replace(DATA_FILE_SUB, data_path))

    return out_path

# Returns all targets read from the file.
# Returns: {predicate: {(atom args): value, ...}, ...}
def _parse_psl_output(out_dir):
    values = {}

    for filename in os.listdir(out_dir):
        path = os.path.join(out_dir, filename)

        if (not os.path.isfile(path)):
            continue

        predicate = os.path.splitext(filename)[0]
        values[predicate] = {}

        with open(path, 'r') as inFile:
            for line in inFile:
                line = line.strip()

                if (line == ''):
                    continue

                parts = line.split("\t")

                args = [int(arg.strip("'")) for arg in parts[0:-1]]
                val = float(parts[-1])

                values[predicate][tuple(args)] = val

    return values

# See if we can get a response for the named database.
def _postgres_database_available(postgresDBName):
    command = "psql '%s' -c ''" % (postgresDBName)

    try:
        subprocess.check_call(command, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, shell = True)
        # print("Postgres successfully discovered.")
    except subprocess.CalledProcessError:
        # print("Postgres not found - using H2 instead.")
        return False

    return True

# Run the PSL model using the CLI and return the output (stdout).
def _run_psl(model_path, data_file_path, run_dir, postgres_db_name = DEFAULT_POSTRGES_DB_NAME):
    logger = get_logger(__name__)

    db_option = ''
    if (postgres_db_name and _postgres_database_available(postgres_db_name)):
        db_option = "--postgres '%s'" % (postgres_db_name)

    out_dir = os.path.join(run_dir, RUN_OUT_DIRNAME)

    memory_bytes = psutil.virtual_memory().total

    args = [
        "java -Xms%d" % (int(memory_bytes * DEFAULT_MEMORY_PERCENT)),
        "-jar '%s'" % (PSL_CLI_JAR),
        "--infer",
        "--model '%s'" % (model_path),
        "--data '%s'" % (data_file_path),
        "--output '%s'" % (out_dir),
        db_option
    ]
    psl_command = " ".join(args)

    logger.debug("Invoking PSL with command: %s", psl_command)

    psl_output = ''
    try:
        psl_output = str(subprocess.check_output(psl_command, shell = True), 'utf-8')
    except subprocess.CalledProcessError as ex:
        print("Failed to run PSL")
        print(psl_output)
        raise ex

    return _parse_psl_output(out_dir)

def _write_predicate_graph(graph, path, graphId):
    rows = []

    for (id, data) in graph.nodes(data = True):
        if (data[SOURCE_GRAPH_KEY] != graphId):
            continue
        rows.append([str(id)])

    write_tsv(path, rows)

def _write_predicate_edge(graph, path, graphId):
    rows = []

    for (source, target, data) in graph.edges(data = True):
        # Skip links.
        if (data[EDGE_TYPE_KEY] != EDGE_TYPE_EDGE):
            continue

        # Skip edges that do not come from out target graph.
        if (graph.node[source][SOURCE_GRAPH_KEY] != graphId):
            continue

        # Edges are undirected.
        rows.append([str(source), str(target), str(data[WEIGHT_KEY])])
        rows.append([str(target), str(source), str(data[WEIGHT_KEY])])

    write_tsv(path, rows)

def _write_predicate_link_observed(graph, path):
    rows = []

    for (source, target, data) in graph.edges(data = True):
        # Skip edges.
        if (data[EDGE_TYPE_KEY] != EDGE_TYPE_LINK):
            continue

        # Skip links that are not observed.
        if (not data[OBSERVED_KEY]):
            continue

        # Make sure graph 1 comes first.
        if (source > target):
            source, target = target, source

        rows.append([str(source), str(target), str(data[WEIGHT_KEY])])

    write_tsv(path, rows)

def _write_predicate_link_prior(graph, path):
    rows = []

    for (source, target, data) in graph.edges(data = True):
        # Skip edges.
        if (data[EDGE_TYPE_KEY] != EDGE_TYPE_LINK):
            continue

        # Skip observed links.
        # Since observed links are not targets, they have no prior.
        if (OBSERVED_KEY in data and data[OBSERVED_KEY]):
            continue

        if (WEIGHT_KEY not in data):
            continue

        # Make sure graph 1 comes first.
        if (source > target):
            source, target = target, source

        rows.append([str(source), str(target), str(data[WEIGHT_KEY])])

    write_tsv(path, rows)

def _write_predicate_link_target(graph, path):
    rows = []

    for (source, target, data) in graph.edges(data = True):
        # Skip edges.
        if (data[EDGE_TYPE_KEY] != EDGE_TYPE_LINK):
            continue

        # Skip observed links.
        if (data[OBSERVED_KEY]):
            continue

        # Make sure graph 1 comes first.
        # TODO(eriq): This should be unnecessary.
        if (source > target):
            source, target = target, source

        rows.append([str(source), str(target)])

    write_tsv(path, rows)

def _write_predicate_block(graph, path):
    rows = []

    for (source, target, data) in graph.edges(data = True):
        # Skip edges.
        if (data[EDGE_TYPE_KEY] != EDGE_TYPE_LINK):
            continue

        # Skip observed links.
        if (data[OBSERVED_KEY]):
            continue

        # Make sure graph 1 comes first.
        # TODO(eriq): This should be unnecessary.
        if (source > target):
            source, target = target, source

        rows.append([str(source), str(target)])

    write_tsv(path, rows)

# Write every possible link that has not been observed.
def _write_predicate_link_target_all(graph, path):
    for (id1, data1) in graph.nodes(data = True):
        if (data1[SOURCE_GRAPH_KEY] != 1):
            continue

        for (id2, data2) in graph.nodes(data = True):
            if (data2[SOURCE_GRAPH_KEY] != 2):
                continue

            # Skip any observed links
            if (graph.has_edge(id1, id2) and graph[id1][id2][OBSERVED_KEY]):
                continue

            rows.append([str(id1), str(id2)])

    write_tsv(path, rows)
