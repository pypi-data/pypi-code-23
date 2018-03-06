# -*- coding: utf-8 -*-

# Copyright 2017 IBM RESEARCH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

"""
DAG Unroller
"""

import networkx as nx

from qiskit.unroll import Unroller
from ._dagbackend import DAGBackend
from ._unrollererror import UnrollerError
from qiskit.qasm._node import Real, Id, IdList, ExpressionList, Gate, \
                              PrimaryList, Int, IndexedId, Qreg, If, Creg, \
                              Program


class DagUnroller(object):
    """An Unroller that takes Dag circuits as the input."""
    def __init__(self, dag_circuit, backend=None):
        if dag_circuit is None:
            raise UnrollerError('Invalid dag circuit!!')

        self.dag_circuit = dag_circuit
        self.backend = backend

    def set_backend(self, backend):
        """Set the backend object."""
        self.backend = backend

    def execute(self):
        """Interpret OPENQASM and make appropriate backend calls."""
        if self.backend is not None:
            self._process()
            return self.backend.get_output()
        else:
            raise UnrollerError("backend not attached")

    def expand_gates(basis=None):
        """Expand all gate nodes to the given basis.

        If basis is empty, each custom gate node is replaced by its
        implementation over U and CX. If basis contains names, then
        those custom gates are not expanded. For example, if "u3"
        is in basis, then the gate "u3" will not be expanded wherever
        it occurs.

        This member function replicates the behavior of the unroller
        module without using the OpenQASM parser.

        basis = list of gate name strings
        """

        if type(self.backend) is not DAGBackend:
            raise UnrollerError("expand_gates only accepts a DAGBackend!!")

        if basis is None:
            basis = self.backend.basis
        # Build the Gate AST nodes for user-defined gates
        gatedefs = []
        for name, gate in self.dag_circuit.gates.items():
            children = [Id(name, 0, "")]
            if gate["n_args"] > 0:
                children.append(ExpressionList(list(
                    map(lambda x: Id(x, 0, ""),
                        gate["args"])
                )))
            children.append(IdList(list(
                map(lambda x: Id(x, 0, ""),
                    gate["bits"])
            )))
            children.append(gate["body"])
            gatedefs.append(Gate(children))
        # Walk through the DAG and examine each node
        builtins = ["U", "CX", "measure", "reset", "barrier"]
        ts = list(nx.topological_sort(self.dag_circuit.multi_graph))
        for node in ts:
            nd = self.dag_circuit.multi_graph.node[node]
            if nd["type"] == "op" and \
               nd["name"] not in builtins + basis and \
               not self.dag_circuit.gates[nd["name"]]["opaque"]:
                subcircuit, wires = self._build_subcircuit(gatedefs,
                                                           basis,
                                                           nd["name"],
                                                           nd["params"],
                                                           nd["qargs"],
                                                           nd["condition"])
                # nx.write_gml(subcircuit.multi_graph,
                #              "subcircuit%d.gml" % node,
                #              stringizer=str)
                self.dag_circuit.substitute_circuit_one(node, subcircuit, wires)
        return self.dag_circuit

    def _build_subcircuit(gatedefs, target_basis,
                          gate_name, gate_params, gate_args,
                          gate_condition):
        """Build DAGCircuit for a given user-defined gate node.

        gatedefs = dictionary of Gate AST nodes for user-defined gates
        target_basis = list of gate names in the target basis
        gate_name = name of gate to expand to target_basis (nd["name"])
        gate_params = list of gate parameters (nd["params"])
        gate_args = list of gate arguments (nd["qargs"])
        gate_condition = None or tuple (string, int) (nd["condition"])

        Returns (subcircuit, wires) where subcircuit is the DAGCircuit
        corresponding to the user-defined gate node expanded to target_basis
        and wires is the list of input wires to the subcircuit in order
        corresponding to the gate's arguments.
        """
        # Build AST for subcircuit
        # gate_params are strings and we want symbols here
        def transform_to_symbols(x):
            x2 = x.replace("^", "**")
            return sympy.sympify(x2)

        gate_params = list(map(transform_to_symbols, gate_params))
        children = [Id(gate_name, 0, "")]
        if len(gate_params) > 0:
            children.append(
                ExpressionList(list(map(lambda x: Real(x), gate_params)))
            )
        new_wires = [("q", j) for j in range(len(gate_args))]
        children.append(
            PrimaryList(
                list(map(lambda x: IndexedId([Id(x[0], 0, ""), Int(x[1])]), new_wires))
            )
        )
        gate_node = CustomUnitary(children)

        id_int = [Id("q", 0, ""), Int(len(gate_args))]
        # Make a list of register declaration nodes
        reg_nodes = [
            Qreg(
                [
                    IndexedId(id_int)
                ]
            )
        ]
        # Add an If node when there is a condition present
        if gate_condition:
            gate_node = If([
                Id(gate_condition[0], 0, ""),
                Int(gate_condition[1]),
                gate_node
            ])
            new_wires += [(gate_condition[0], j)
                          for j in range(self.cregs[gate_condition[0]])]
            reg_nodes.append(
                Creg([
                    IndexedId([
                        Id(gate_condition[0], 0, ""),
                        Int(self.cregs[gate_condition[0]])
                    ])
                ])
            )

        # Build the whole program's AST
        sub_ast = Program(gatedefs + reg_nodes + [gate_node])
        # Interpret the AST to give a new DAGCircuit over target_basis
        u = Unroller(sub_ast, self.backend(target_basis))
        subcircuit = u.execute()
        return subcircuit, new_wires


    def _process():
        for name, width in self.dag_circuit.qregs.items():
            self.backend.new_qreg(name, width)
        for name, width in self.dag_circuit.cregs.items():
            backend.new_creg(name, width)
        for name, data in self.dag_circuit.gates.items():
            self.backend.define_gate(name, data)
        for n in nx.topological_sort(self.dag_circuit.multi_graph):
            nd = self.dag_circuit.multi_graph.node[n]
            if nd["type"] == "op":
                def transform_to_real(x):
                    x2 = x.replace("^", "**")
                    x3 = sympy.sympify(x2)
                    return Real(x3)
                # nd["params"] are strings but here we want Real expressions
                params = list(map(transform_to_real, nd["params"]))
                if nd["condition"] is not None:
                    self.backend.set_condition(nd["condition"][0],
                                               nd["condition"][1])
                if not nd["cargs"]:
                    if nd["name"] == "U":
                        self.backend.u(params, nd["qargs"][0])
                    elif nd["name"] == "CX":
                        self.backend.cx(nd["qargs"][0], nd["qargs"][1])
                    elif nd["name"] == "barrier":
                        self.backend.barrier([nd["qargs"]])
                    elif nd["name"] == "reset":
                        self.backend.reset(nd["qargs"][0])
                    else:
                        self.backend.start_gate(nd["name"], params,
                                                nd["qargs"])
                        self.backend.end_gate(nd["name"], params, nd["qargs"])
                else:
                    if nd["name"] == "measure":
                        if len(nd["cargs"]) != 1 or len(nd["qargs"]) != 1 \
                                or nd["params"]:
                                raise UnrollerError("Bad node data!!")

                        self.backend.measure(nd["qargs"][0], nd["cargs"][0])
                    else:
                        raise UnrollerError("Bad node data!")

                self.backend.drop_condition()
        return self.backend.get_output()
