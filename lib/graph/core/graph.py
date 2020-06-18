from collections import defaultdict
from .edge import Edge


class Graph:
    def __init__(self):
        self._nodes = []
        self._edges = []

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    def create_node(self, node_class, **kwargs):
        node = node_class(self, **kwargs)
        self.add_node(node)
        return node

    def create_edge(self, src, dst, relation):
        edge = Edge(self, src, dst, relation)
        self.add_edge(edge)
        return edge

    def add_node(self, node):
        self._nodes.append(node)

    def add_edge(self, edge):
        self._edges.append(edge)
