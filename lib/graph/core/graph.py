from collections import defaultdict
from .edge import Edge


class Graph:
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
