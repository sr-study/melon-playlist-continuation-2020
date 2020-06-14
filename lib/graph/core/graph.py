from collections import defaultdict
from .edge import Edge


class Graph:
    def __init__(self):
        self._nodes = []
        self._edges = []
        self._in_edges = defaultdict(set)
        self._out_edges = defaultdict(set)

    def add_node(self, node_class, **kwargs):
        node = node_class(self, **kwargs)
        self._nodes.append(node)
        return node

    def add_edge(self, src, dst, edge_type):
        edge = Edge(self, src, dst, edge_type)
        self._edges.append(edge)
        self._in_edges[dst].add(edge)
        self._out_edges[src].add(edge)
        return edge
