from tqdm import tqdm
from collections import defaultdict


class CachedGraph:
    def __init__(self, graph):
        self._graph = None

        self._initialize(graph)

    @property
    def nodes(self):
        return self._nodes.values()

    @property
    def edges(self):
        return self._edges.values()

    def get_node(self, node_class, id):
        return self._class_nodes[node_class][id]

    def _initialize(self, graph):
        self._graph = graph

        self._nodes = {}
        self._class_nodes = {}
        self._edges = {}
        self._node_edges = defaultdict(list)
        self._node_relation_edges = defaultdict(list)

        self._register_nodes(self._graph.nodes)
        self._register_edges(self._graph.edges)

    def _register_nodes(self, nodes):
        for node in tqdm(nodes, "Cache nodes"):
            node_proxy = CachedGraph.NodeProxy(self, node)
            node_class = node_proxy.get_class()
            self._nodes[node] = node_proxy
            self._class_nodes[node_class, node_proxy.id] = node_proxy

    def _register_edges(self, edges):
        for edge in tqdm(edges, "Cache edges"):
            edge_proxy = CachedGraph.EdgeProxy(self, edge)
            self._edges[edge] = edge_proxy
            src = edge_proxy.src
            relation = edge_proxy.relation
            self._node_edges[src].append(edge)
            self._node_relation_edges[src, relation].append(edge)

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
            edges = self.get_related_edges(relation)
            return [edge.dst for edge in edges]

        def _foward_public_attributes(self, obj):
            public_attrs = filter(lambda x: not x.startswith('_'), dir(obj))
            for attr in public_attrs:
                if not hasattr(self, attr):
                    setattr(self, attr, getattr(obj, attr))

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
