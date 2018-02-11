"""
Representation of rules in a Decision Tree (scikit-learn)
Copyright (C) 2017 - Pietro Mascolo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Pietro Mascolo
Email: iz4vve@gmail.com
"""
import json
import sklearn


def extract_rules(tree, feature_names=None):
    """
    Extracts rule set from decision tree and returns it as a json string
    Does not rely directly the json library due to its notorious difficulties
    in dealing with small floating point numbers.

    :param tree: a decision tree
    :param feature_names: names of the classes of the tree (optional)
    :type feature_names: dict
    :return: rule set of the decision tree
    :rtype: json string
    """

    js = ""

    def node_to_str(tree, node_id, criterion):
        if not isinstance(criterion, sklearn.tree.tree.six.string_types):
            criterion = "impurity"

        value = tree.value[node_id]

        if tree.n_outputs == 1:
            value = value[0, :]

        json_tree = ','.join([str(x) for x in value])

        if tree.children_left[node_id] == sklearn.tree._tree.TREE_LEAF:
            ret = ",".join(['"id": "{}"',
                            '"criterion": "{}"',
                            ' "impurity": "{}"',
                            '"samples": "{}"',
                            '"value": [{}]'])
            return ret.format(
                node_id,
                criterion,
                tree.impurity[node_id],
                tree.n_node_samples[node_id],
                json_tree
            )

        else:
            feature = feature_names[tree.feature[node_id]] \
                if feature_names is not None else tree.feature[node_id]
            rule_type = "=" if "=" in str(feature) else "<="
            rule_value = "false" if "=" in str(feature) \
                else "%.4f" % tree.threshold[node_id]

        ret = ",".join(['"id": "{}"',
                        '"rule": "{} {} {}"',
                        '"{}": "{}"',
                        '"samples": "{}"'])
        return ret.format(
            node_id,
            feature,
            rule_type,
            rule_value,
            criterion,
            tree.impurity[node_id],
            tree.n_node_samples[node_id]
        )

    def recurse(tree, node_id, criterion, parent=None, depth=0):
        js = ""

        left_child = tree.children_left[node_id]
        right_child = tree.children_right[node_id]

        js = js + "{" + node_to_str(tree, node_id, criterion)

        if left_child != sklearn.tree._tree.TREE_LEAF:
            js = js + "," + '  "left": ' + recurse(
                tree,
                left_child,
                criterion=criterion,
                parent=node_id,
                depth=depth + 1
            ) + "," + '"right": ' + recurse(\
                tree,
                right_child,
                criterion=criterion,
                parent=node_id,
                depth=depth + 1
            )

        js += "}"

        return js

    if isinstance(tree, sklearn.tree.tree.Tree):
        js += recurse(tree, 0, criterion="impurity")
    else:
        js += recurse(tree.tree_, 0, criterion=tree.criterion)

    return json.loads(js)


def export_graph(model, path='tree.dot', names=None):
    from sklearn import tree

    tree.export_graphviz(model, out_file=path, feature_names=names)
