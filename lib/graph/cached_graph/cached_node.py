from collections import defaultdict


class CachedNode:
    def __init__(self, index, node):
        self.node_class = node.__class__
        self.id = node.id

        self._index = index
        self._edges = []
        self._relation_edges = defaultdict(list)
        self._neighbor_nodes = []
        self._relation_nodes = defaultdict(list)

        self._foward_public_attributes(node)

    def add_edge(self, edge):
        self._edges.append(edge)
        self._relation_edges[edge.relation].append(edge)
        self._neighbor_nodes.append(edge.dst)
        self._relation_nodes[edge.relation].append(edge.dst)

    def get_related_edges(self, relation=None):
        if relation is None:
            return self._edges
        else:
            return self._relation_edges[relation]

    def get_related_nodes(self, relation=None):
        if relation is None:
            return self._neighbor_nodes
        else:
            return self._relation_nodes[relation]

    def _foward_public_attributes(self, obj):
        public_attrs = filter(lambda x: not x.startswith('_'), dir(obj))
        for attr in public_attrs:
            if not hasattr(self, attr):
                setattr(self, attr, getattr(obj, attr))

    def __str__(self):
        return repr(self)

    def __repr__(self):
        class_name = self.__class__.__name__
        node_class_name = self.node_class.__qualname__
        return f"<{class_name}({node_class_name}) object at {hex(id(self))}>"
