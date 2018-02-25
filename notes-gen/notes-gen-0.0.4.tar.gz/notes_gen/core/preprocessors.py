import os
import re

import networkx as nx

from notes_gen.core.exceptions import MarkdownException


class BasePrePorcessor:

    def execute(self, site):
        '''This function will be called in preprocessor state.
        '''
        raise NotImplementedError('Subclass of BasePreProcessor must implement execute method.')


class MarkdownCombiner(BasePrePorcessor):
    '''Preprocessor which parses include driective from markdown and then replace it with appropriate content.
    It does this by creating a dependency graph for the files.
    '''

    _KEY_CLEANUP = 'cleanup'
    _KEY_MARKDOWN_FILE = 'markdown_files'

    _COMBINED_FILENAME = '_combined.md'

    _INCLUDE_REGEX = r"```include(?P<content>[\s\S]*?\n)```"

    _error_messages = {
        'invalid_path': 'Invalid include path "{path}" in file "{file_path}"',
        'recursive_include': 'Recursive includes are not allowed. {cycle}',
    }

    def _get_graph_content(self, file_path):
        '''Parse markdown and build a graph node with following content
        [
            "content before include",
            [
                "file1.md",
                "file2.md"
            ],
            "content after include"

        ]
        '''

        with open(file_path, 'r') as file:
            content = file.read()

        graph_content = []

        match = re.search(self._INCLUDE_REGEX, content)
        # Construct content
        while match is not None:
            # Add before content
            graph_content.append(content[:match.start()])

            # Add includes
            include_files = []
            for line in match.group('content').strip().splitlines():

                line = line.strip()
                if len(line) == 0:
                    continue

                # Check if file exists
                line = os.path.abspath(os.path.join(os.path.dirname(file_path), line))
                if os.path.isfile(line) is False:
                    msg = self._error_messages['invalid_path'].format(path=line, file_path=file_path)
                    raise MarkdownException(msg)

                include_files.append(line)

            if len(include_files) > 0:
                graph_content.append(include_files)

            # Find next include
            content = content[match.end():]
            match = re.search(self._INCLUDE_REGEX, content)

        # Add remaing content
        if len(content) > 0:
            graph_content.append(content)

        return graph_content

    def _build_graph(self, file_path, graph=None):
        '''Build Dependency graph from give node
        '''
        if graph is None:
            graph = nx.DiGraph()

        # Add node only if node is not present
        if graph.has_node(file_path) is True:
            return graph

        # Add graph node
        content = self._get_graph_content(file_path)
        graph.add_node(file_path, content=content)

        # Call recusively for each include
        for item in content:
            if isinstance(item, list) is False:
                continue

            for include_file in item:
                self._build_graph(include_file, graph=graph)

                # Add graph edge
                graph.add_edge(file_path, include_file)

                # Check if cycle
                cycle = [_ for _ in nx.simple_cycles(graph)]
                if len(cycle) > 0:
                    cycle = cycle[0]
                    cycle.append(cycle[0])
                    cycle_string = ' => '.join(cycle)
                    raise MarkdownException(self._error_messages['recursive_include'].format(cycle=cycle_string))

        return graph

    def _substitue_leaf_node_into_parent(self, graph, parent_node, child_node):
        '''Substitue the content of child in parent. Assuming child_node is leaf node with no include list
        '''
        parent_content = graph.nodes[parent_node]['content']
        child_content = '\n'.join(graph.nodes[child_node]['content'])

        new_parent_content = []
        for item in parent_content:
            # Only process include list
            if isinstance(item, list) is False:
                new_parent_content.append(item)
                continue

            # Loop include list and divide list if include is present
            new_includes = []
            for file_path in item:

                # Add before include and then add child content. Divide the list if
                if file_path == child_node:
                    if len(new_includes) > 0:
                        new_parent_content.append(new_includes)
                    new_parent_content.append(child_content)
                    new_includes = []
                # Else add include list
                else:
                    new_includes.append(file_path)

            if len(new_includes) > 0:
                new_parent_content.append(new_includes)

        # Update parent node content
        graph.add_node(parent_node, content=new_parent_content)

    def _combine_graph(self, graph, file_path):
        '''Combine graph into one content starting from leave node
        '''

        while len(graph.nodes) != 1:

            leaf_node = [node for node in graph.node if graph.out_degree(node) == 0][0]

            # Substitue leaf_node content in parent node
            for node in graph.predecessors(leaf_node):
                self._substitue_leaf_node_into_parent(graph, node, leaf_node)

            # Remove leaf node
            graph.remove_node(leaf_node)

        # Combined last node data
        combined_content = [(node, data) for node, data in graph.nodes.data()][0][1]['content']
        combined_content = '\n'.join(combined_content)

        # Write combined content to the file
        with open(file_path, 'w') as file:
            file.write(combined_content)

    def _combine_markdown(self, file_path):
        '''Combine a give markdown file with include into single file.
        First build a dependency graph without cycle and then,
        Combine the graph into single node with content.
        '''
        combined_file_path = os.path.join(os.path.dirname(file_path), self._COMBINED_FILENAME)

        graph = self._build_graph(file_path)
        self._combine_graph(graph, combined_file_path)

        return combined_file_path

    def execute(self, site):
        '''Combine markdown which have include directive in it
        '''

        # Get main markdown file
        main_mardown_files = [
            item.copy() for item in site[self._KEY_MARKDOWN_FILE] if item.get('meta', {}).get('main', False) is True
        ]

        # Create a combined markdown file
        combined_files = []
        for file in main_mardown_files:
            file['path'] = self._combine_markdown(file['path'])
            combined_files.append(file)

        # Add autogenerated file in cleanup
        site[self._KEY_CLEANUP] = site.get(self._KEY_CLEANUP, []) + [file['path'] for file in combined_files]

        # Replace markdown file with _combined file
        site[self._KEY_MARKDOWN_FILE] = combined_files
