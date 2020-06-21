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

    def _initialize(self, graph):
        self.nodes = []
        self.edges = []
        self._class_nodes = {}

        self._add_nodes(graph.nodes)
        self._add_edges(graph.edges)

    def _add_nodes(self, nodes):
        for node in tqdm(nodes, "Caching nodes"):
            self._add_node(node)

    def _add_edges(self, edges):
        for edge in tqdm(edges, "Caching edges"):
            self._add_edge(edge)

    def _add_node(self, node):
        index = len(self.nodes)
        cached_node = CachedNode(index, node)
        self.nodes.append(cached_node)
        self._class_nodes[cached_node.node_class, cached_node.id] = cached_node

    def _add_edge(self, edge):
        src = self.get_node(edge.src.__class__, edge.src.id)
        dst = self.get_node(edge.dst.__class__, edge.dst.id)
        relation = edge.relation

        cached_edge = CachedEdge(src, dst, relation)
        self.edges.append(cached_edge)
        src.add_edge(cached_edge)
