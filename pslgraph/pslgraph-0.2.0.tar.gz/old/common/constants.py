import os

PSL_CLI_DIR = os.path.join(os.path.dirname(__file__), 'psl-cli')
PSL_CLI_JAR = os.path.join(PSL_CLI_DIR, 'psl-cli-CANARY.jar')
DEFAULT_POSTRGES_DB_NAME = 'psl'

DEFAULT_DATA_DIR = 'data'

GRAPH1_PREDICATE_FILENAME = 'graph1_obs.txt'
GRAPH2_PREDICATE_FILENAME = 'graph2_obs.txt'
EDGE1_PREDICATE_FILENAME = 'edge1_obs.txt'
EDGE2_PREDICATE_FILENAME = 'edge2_obs.txt'
LINK_PRIOR_PREDICATE_FILENAME = 'link_prior_obs.txt'
LINK_PREDICATE_OBS_FILENAME = 'link_obs.txt'
LINK_PREDICATE_TARGET_FILENAME = 'link_target.txt'

NODE_ID_LABEL = 'nodeID'
D3MINDEX_COLUMN_NAME = 'd3mIndex'

# Keys for properties on nodes and edges.
SOURCE_GRAPH_KEY = 'sourceGraph'
WEIGHT_KEY = 'weight'
EDGE_TYPE_KEY = 'edgeType'
OBSERVED_KEY = 'observed'

COMPUTED_SOURCE_COSINE = 'computed_cosine'
COMPUTED_SOURCE_LOCAL_SIM = 'computed_localsim'
COMPUTED_SOURCE_MEAN = 'computed_mean'

# We call edges between nodes in the same graph "edges".
EDGE_TYPE_EDGE = 'edge'
# We call edges between nodes in different graphs "links".
EDGE_TYPE_LINK = 'link'

# Graph hints that upstream graph constructors can pass to the graph transformer.

# Compute the local (feature-based) similarity between graphs for link priors.
GRAPH_HINT_LINK_LOCAL_SIM = 'linkPriorLocalSim'
# Compute link priors using the mean of all other links the source/dest nodes participate in.
GRAPH_HINT_LINK_MEAN = 'linkPriorMean'
# Compute edges (weights for non-existant edges) using the cosine similairty based off of the links the nodes participate in.
GRAPH_HINT_EDGE_COSINE = 'edgeCosine'
