import os

DEBUG_OPTION_LOGGING_LEVEL = 'logging_level'
DEBUG_OPTION_RUN_FAST = 'run_fast'

# PSL-related constants.

PSL_CLI_DIR = os.path.join(os.path.dirname(__file__), 'psl-cli')
PSL_CLI_JAR = os.path.join(PSL_CLI_DIR, 'psl-cli-CANARY-2.1.1.jar')
RUN_OUT_DIRNAME = 'psl-out'

LINK_PREDICATE = 'LINK'

GRAPH1_PREDICATE_FILENAME = 'graph1_obs.txt'
GRAPH2_PREDICATE_FILENAME = 'graph2_obs.txt'
EDGE1_PREDICATE_FILENAME = 'edge1_obs.txt'
EDGE2_PREDICATE_FILENAME = 'edge2_obs.txt'
LINK_PRIOR_PREDICATE_FILENAME = 'link_prior_obs.txt'
LINK_PREDICATE_OBS_FILENAME = 'link_obs.txt'
LINK_PREDICATE_TARGET_FILENAME = 'link_target.txt'
BLOCK_PREDICATE_FILENAME = 'block_obs.txt'

NODE_ID_LABEL = 'nodeID'

NODE_MODIFIER_SOURCE = -1
NODE_MODIFIER_TARGET = +1

# Keys for properties on nodes and edges.
SOURCE_GRAPH_KEY = 'sourceGraph'
WEIGHT_KEY = 'weight'
EDGE_TYPE_KEY = 'edgeType'
OBSERVED_KEY = 'observed'
INFERRED_KEY = 'inferred'
TARGET_KEY = 'inferenceTarget'

# We call edges between nodes in the same graph "edges".
EDGE_TYPE_EDGE = 'edge'
# We call edges between nodes in different graphs "links".
EDGE_TYPE_LINK = 'link'

COMPUTED_SOURCE_COSINE = 'computed_cosine'
COMPUTED_SOURCE_LOCAL_SIM = 'computed_localsim'
COMPUTED_SOURCE_MEAN = 'computed_mean'

# Graph hints that upstream graph constructors can pass to the graph transformer.

# Compute the local (feature-based) similarity between graphs for link priors.
GRAPH_HINT_LINK_LOCAL_SIM = 'linkPriorLocalSim'
# Compute link priors using the mean of all other links the source/dest nodes participate in.
GRAPH_HINT_LINK_MEAN = 'linkPriorMean'
# Compute edges (weights for non-existant edges) using the cosine similairty based off of the links the nodes participate in.
GRAPH_HINT_EDGE_COSINE = 'edgeCosine'

GRAPH_MATCHING_DATASET_TABLE_INDEX = '2'
