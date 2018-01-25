import os
import re
import json
import uuid
import tempfile
from IPython.display import HTML, Javascript, display

DEFAULT_PHYSICS = {
    "physics": {
        "enabled": False
    }
}



def init_notebook_mode():
    """
    Creates a script tag and prints the JS read from the file in the tag.
    """

    display(
        Javascript(data="require.config({ " +
                        "    paths: { " +
                        "        vis: '//cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min' " +
                        "    } " +
                        "}); " +
                        "require(['vis'], function(vis) { " +
                        " window.vis = vis; " +
                        "}); ",
                   css='https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.css')
        )


def vis_network(nodes, edges, physics=DEFAULT_PHYSICS):
    """
    Creates the HTML page with all the parameters
    :param nodes: The nodes to be represented an their information.
    :param edges: The edges represented an their information.
    :param physics: The options for the physics of vis.js.
    :return: IPython.display.HTML
    """
    base = open(os.path.join(os.path.dirname(__file__), 'assets/index.html')).read()

    unique_id = str(uuid.uuid4())
    html = base.format(id=unique_id, nodes=json.dumps(nodes), edges=json.dumps(edges), physics=json.dumps(physics))

    return HTML(html)


def draw(data, options={}, physics=True):
    """
    The options argument should be a dictionary of node labels and property keys; it determines which property
    is displayed for the node label. For example, in the movie graph, options = {"Movie": "title", "Person": "name"}.
    Omitting a node label from the options dict will leave the node unlabeled in the visualization.
    Setting physics = True makes the nodes bounce around when you touch them!

    AgensGraph return should be:

    [ table
        ( rows
            {}/[] columns...
        )...
    ]


    :param data: Data from the DB query.
    :param options: Options for the Nodes.
    :param physics: Physics of the vis.js visualization.
    :return: IPython.display.HTML
    """

    nodes = []
    edges = []
    nodes_ids = set()

    def _check_node(node):

        if node.get("vid", False) and  node["vid"] not in nodes_ids:
            nodes.append({
                "id": node["vid"],
                "label": re.sub("[\(\[].*?[\)\]]" , "", node["term"]),
                "group": node["label"],
                "title": node["term"]
            })
            nodes_ids.add(node["vid"])

    for row in data:

        source_node = None
        target_node = None
        rel = None

        for element in row:
            if element.get("type", False) == "vertex":
                _check_node(element)

            elif element.get("type", False) == "edge":
                rel = {
                    "from": element["source_vid"],
                    "to": element["destination_vid"],
                    "label": element["label"]}
                if rel not in edges:
                    edges.append(rel)

            elif element.get("type", False) == "path":
                for n in element["vertices"]:
                    _check_node(n)
                for e in element["edges"]:
                    rel = {
			"from": e["source_vid"],
			"to": e["destination_vid"],
			"label": e["label"]}
                    if rel not in edges:
                        edges.append(rel)

            elif type(element) is list and len(element) >= 1:
                for r in element:
                    rel = {"from": r["source_vid"], "to": r["destination_vid"], "label": r["label"]}
                    if rel not in edges:
                        edges.append(rel)

    return vis_network(nodes, edges, physics=physics)
