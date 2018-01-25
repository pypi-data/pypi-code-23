# TODO(eriq): Deprecated. Remove once ISI is migrated.

from typing import *
from gevent import os
from d3m_types.base import Graph
from primitive_interfaces.graph import GraphTransformerPrimitiveBase

from .decomposeGraph import processFiles
from .processData_049_toGML import processData
from .processData_049_toGML import GRAPH_PATH
from .processData_049_toGML import TARGETS_PATH
from .util import runPSL
from .util import getTopLinksFromPSL

from pandas import DataFrame

Inputs = TypeVar('Inputs', bound=Sequence[Graph])
Outputs = TypeVar('Outputs', bound=Sequence[Graph])

GRAPH_INDEX = 0
NODEID_INDEX = 1

class PSLGraphPrimitive(GraphTransformerPrimitiveBase[Inputs, Outputs]):

    # HACK(eriq): Just make this work for now, forget about the GraphAPI.

    def __init__(self, embedded_features = True) -> None:
        self._embedded_features = embedded_features
        self._graph1 = None
        self._graph2 = None
        self._crosspartEdes = None
        self._bestLinks = None

    # def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
    def set_training_data(self, inputs, outputs):
        assert len(inputs) == len(outputs)

        self._crosspartEdges = []

        for (d3mIndex, row) in inputs.iterrows():
            if (self._graph1 == None):
                self._graph1 = row[GRAPH_INDEX]

            if (self._graph2 == None):
                self._graph2 = outputs.loc[d3mIndex][GRAPH_INDEX]

            # HACK(eriq): This is ingraned futher down in our code, but we should see if we actually need this (context ids).
            source = "%s::%s" % ('1', inputs.loc[d3mIndex][NODEID_INDEX])
            target = "%s::%s" % ('2', outputs.loc[d3mIndex][NODEID_INDEX])

            self._crosspartEdges.append((source, target))
            self._crosspartEdges.append((target, source))

    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if (self._graph1 == None):
            raise "Call set_training_data() before fit()."

        if (not self._embedded_features):
            raise "Only embedded features are currently supported."

        # Convert the data into a unified GML format.
        if (self._embedded_features):
            processData(self._graph1, self._graph2, self._crosspartEdges)

        # Convert the GML into the PSL format.
        processFiles(GRAPH_PATH, TARGETS_PATH)

        # Run the "unified" model in PSL.
        pslOutput = runPSL('unified-old')

        # TODO(eriq): We should probably save all the links for when people want
        #  all the information.
        # Parse the output and save the best links.
        self._bestLinks = getTopLinksFromPSL(pslOutput)

    def produce(self, inputs, timeout: float = None, iterations: int = None):
        if (self._bestLinks == None):
            raise "Call fit() before produce()."

        results = DataFrame(columns=('graph', 'nodeID'))

        for (d3mIndex, row) in inputs.iterrows():
            nodeId = row[NODEID_INDEX]
            results.loc[d3mIndex] = [self._graph2, self._bestLinks[nodeId]]
            
        return results

    """
    This is the main PSL Graph Primitive. The first step is to examine the input data to verify it is valid. Next
    it will be written to disk for use by the PSL program which will be invoked using the CLI interface. Once complete
    the results will be read back in from disk and returned to the caller in the expected format.
    """

    '''
    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:
        print("PSLGraphPrimitive::Produce Called...")

        # First, Inspect the Graph data to make sure it is usable by this Primitive
        # TODO: Are there other validation steps that we should take?
        if (inputs._directed) :
            print("Error, the primitive is unable to process directed graphs")
            return

        # Second, get the filename that the graph was loaded from
        filename = inputs._graph_filename

        # Third, pass the graph data to PSL with the CLI
        # FNULL = open(os.devnull, 'w')  # use this if you want to suppress output to stdout from the subprocess
        # args = ["java", "-jar", "/Users/daraghhartnett/Projects/D3M/code/psl-ta1/docker/psl-cli-CANARY.jar", "-infer",
        #         "-model", "graph-link-completion.psl", "-data ", "filename"]
        # subprocess.call(args, stdin=subprocess.DEVNULL, stdout=subprocess.STDOUT, stderr=FNULL, shell=False)

        # If this does not block figure out why the subprocess call above does not work
        # os.system("java -jar docker/psl-cli-CANARY.jar -infer -model graph-link-completion.psl -data " + filename)

        # Third, read the results back in and pass back to the caller.
    '''

