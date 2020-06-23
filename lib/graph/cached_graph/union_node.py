from collections import defaultdict
from .cached_node import CachedNode


class UnionNode(CachedNode):
    def __init__(self, index, nodes):
        self.index = index
        self.node_class = tuple([node.__class__ for node in nodes])
        self.id = tuple([node.id for node in nodes])

        self._edges = []
        self._relation_edges = defaultdict(list)
        self._neighbor_nodes = []
        self._relation_nodes = defaultdict(list)

        self.nodes = tuple([node for node in nodes])
