from .cached_node import CachedNode
from ..graph import Graph


class CachedGraph:
    def __init__(self, graph):
        self.nodes = []
        self._cache(graph)

    def _cache(self, graph):
        cached_nodes = []

        for node in graph.nodes:
            index = len(cached_nodes)
            cached_node = CachedNode(node.type, node.id, node.data, index)
            cached_nodes.append(cached_node)

        for edge in graph.edges:
            src = cached_nodes[edge.src]
            dst = cached_nodes[edge.dst]
            relation = edge.relation
            src.add_related_node(dst, relation)

        self.nodes = cached_nodes

    def state(self):
        return {
            'nodes': self._create_node_states(),
            'edges': self._create_edge_states(),
        }

    def _create_node_states(self):
        return [node.state() for node in self.nodes]

    def _create_edge_states(self):
        edge_states = []
        for node in self.nodes:
            for relation, related_nodes in node.related_nodes.items():
                for related_node in related_nodes:
                    src = node.index
                    dst = related_node.index
                    edge_state = (src, dst, relation)
                    edge_states.append(edge_state)

        return edge_states
