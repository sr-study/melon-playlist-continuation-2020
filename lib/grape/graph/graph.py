from typing import List
from .edge import Edge
from .node import Node


class Graph:
    class NodeType:
        _auto_id = 0

        @classmethod
        def auto(cls):
            cls._auto_id += 1
            return cls._auto_id

    class Relation:
        _auto_id = 0

        @classmethod
        def auto(cls):
            cls._auto_id += 1
            return cls._auto_id

    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def add_nodes(self, nodes):
        self.nodes += nodes

    def add_edges(self, edges):
        self.edges += edges

    def state(self):
        return {
            'nodes': [node.state() for node in self.nodes],
            'edges': [edge.state() for edge in self.edges],
        }

    @classmethod
    def from_state(cls, state):
        graph = Graph()
        graph.nodes = [Node.from_state(s) for s in state['nodes']]
        graph.edges = [Edge.from_state(s) for s in state['edges']]
        return graph
