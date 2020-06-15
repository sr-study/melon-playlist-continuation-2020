from collections import defaultdict
from .edge import Edge


class Graph:
    def __init__(self):
        self._nodes = []
        self._edges = []
        self._in_edges = defaultdict(list)
        self._out_edges = defaultdict(list)

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    def add_node(self, node_class, **kwargs):
        node = node_class(self, **kwargs)
        self._nodes.append(node)
        return node

    def add_edge(self, src, dst, relation):
        edge = Edge(self, src, dst, relation)
        self._edges.append(edge)
        self._in_edges[dst].append(edge)
        self._out_edges[src].append(edge)
        return edge