from tqdm import tqdm
from .cached_node import CachedNode
from .cached_edge import CachedEdge


class CachedGraph:
    def __init__(self, graph):
        self._initialize(graph)

    def has_node(self, node_class, node_id):
        return (node_class, node_id) in self._class_nodes

    def get_node(self, node_class, node_id):
        return self._class_nodes[node_class, node_id]

    def get_nodes(self, node_class, ids):
        return [self.get_node(node_class, node_id)
                for node_id in ids if self.has_node(node_class, node_id)]

    def add_node(self, cached_node):
        self.nodes.append(cached_node)
        self._class_nodes[cached_node.node_class, cached_node.id] = cached_node

    def add_edge(self, cached_edge):
        self.edges.append(cached_edge)
        cached_edge.src.add_edge(cached_edge)

    def _initialize(self, graph):
        self.nodes = []
        self.edges = []
        self._class_nodes = {}

        self._cache_nodes(graph.nodes)
        self._cache_edges(graph.edges)

    def _cache_nodes(self, nodes):
        for node in tqdm(nodes, "Caching nodes"):
            self._cache_node(node)

    def _cache_edges(self, edges):
        for edge in tqdm(edges, "Caching edges"):
            self._cache_edge(edge)

    def _cache_node(self, node):
        index = len(self.nodes)
        cached_node = CachedNode(index, node)
        self.add_node(cached_node)

    def _cache_edge(self, edge):
        src = self.get_node(edge.src.__class__, edge.src.id)
        dst = self.get_node(edge.dst.__class__, edge.dst.id)
        relation = edge.relation

        cached_edge = CachedEdge(src, dst, relation)
        self.add_edge(cached_edge)
