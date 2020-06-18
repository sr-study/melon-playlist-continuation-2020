from tqdm import tqdm
from collections import defaultdict


class CachedGraph:
    def __init__(self, graph):
        self._initialize(graph)

    @property
    def nodes(self):
        return list(self._nodes.values())

    @property
    def edges(self):
        return list(self._edges.values())

    def has_node(self, node_class, id_):
        return ((node_class, id_) in self._class_nodes)

    def get_node(self, node_class, id_, noneable=False):
        if noneable:
            try:
                return self._class_nodes[node_class, id_]
            except KeyError:
                return None
        else:
            return self._class_nodes[node_class, id_]

    def get_nodes(self, node_class, ids, ignore_none=False):
        if ignore_none:
            return [self.get_node(node_class, id_)
                    for id_ in ids if self.has_node(node_class, id_)]
        else:
            return [self.get_node(node_class, id_) for id_ in ids]

    def _initialize(self, graph):
        self._graph = graph

        self._nodes = {}
        self._class_nodes = {}
        self._edges = {}
        self._node_edges = defaultdict(list)
        self._node_relation_edges = defaultdict(list)
        self._node_neighbor_nodes = defaultdict(list)
        self._node_relation_nodes = defaultdict(list)

        self._register_nodes(self._graph.nodes)
        self._register_edges(self._graph.edges)

    def _register_nodes(self, nodes):
        for node in tqdm(nodes, "Caching nodes"):
            node_proxy = CachedGraph.NodeProxy(self, node)
            node_class = node_proxy.get_class()
            self._nodes[node] = node_proxy
            self._class_nodes[node_class, node_proxy.id] = node_proxy

    def _register_edges(self, edges):
        for edge in tqdm(edges, "Caching edges"):
            edge_proxy = CachedGraph.EdgeProxy(self, edge)
            self._edges[edge] = edge_proxy
            src = edge_proxy.src
            dst = edge_proxy.dst
            relation = edge_proxy.relation
            self._node_edges[src].append(edge_proxy)
            self._node_relation_edges[src, relation].append(edge_proxy)
            self._node_neighbor_nodes[src].append(dst)
            self._node_relation_nodes[src, relation].append(dst)

    class NodeProxy:
        def __init__(self, graph, node):
            self._graph = graph
            self._node = node
            self._foward_public_attributes(node)

        @property
        def id(self):
            return self._node.id

        def get_class(self):
            return self._node.__class__

        def get_related_edges(self, relation=None):
            if relation is None:
                return self._graph._node_edges[self]
            else:
                return self._graph._node_relation_edges[self, relation]

        def get_related_nodes(self, relation=None):
            if relation is None:
                return self._graph._node_neighbor_nodes[self]
            else:
                return self._graph._node_relation_nodes[self, relation]

        def _foward_public_attributes(self, obj):
            public_attrs = filter(lambda x: not x.startswith('_'), dir(obj))
            for attr in public_attrs:
                if not hasattr(self, attr):
                    setattr(self, attr, getattr(obj, attr))

        def __str__(self):
            return repr(self)

        def __repr__(self):
            class_name = self.__class__.__name__
            node_class_name = self.get_class().__qualname__
            return f"<{class_name}({node_class_name}) object at {hex(id(self))}>"

    class EdgeProxy:
        def __init__(self, graph, edge):
            self._graph = graph
            self._edge = edge
            self._src = self._graph._nodes[edge.src]
            self._dst = self._graph._nodes[edge.dst]
            self._relation = edge.relation

        @property
        def src(self):
            return self._src

        @property
        def dst(self):
            return self._dst

        @property
        def relation(self):
            return self._relation
