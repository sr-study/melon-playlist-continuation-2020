from tqdm import tqdm
from collections import defaultdict
from .cached_node import CachedNode
from ..graph import Graph
from ..utils import TqdmDummy


class CachedGraph:
    def __init__(self, graph, verbose=True):
        self.nodes = []
        self.type_node_dict = defaultdict(dict)
        self._cache(graph, verbose)

    def has_node(self, node_type, node_id):
        return node_id in self.type_node_dict[node_type]

    def get_node(self, node_type, node_id):
        return self.type_node_dict[node_type][node_id]

    def get_nodes(self, node_type, node_ids):
        return [self.type_node_dict[node_type][node_id]
                for node_id in node_ids
                if node_id in self.type_node_dict[node_type]]

    def get_all_nodes(self, node_type):
        return list(self.type_node_dict[node_type].values())

    def state(self):
        return {
            'nodes': self._create_node_states(),
            'edges': self._create_edge_states(),
        }

    def _cache(self, graph, verbose=True):
        if verbose:
            total = len(graph.nodes) + len(graph.edges) + len(graph.nodes)
            pbar = tqdm(desc="Caching graph", total=total)
        else:
            pbar = TqdmDummy()

        with pbar:
            self.nodes = self._create_cached_nodes(graph, pbar)

            for node in self.nodes:
                self.type_node_dict[node.type][node.id] = node

                pbar.update()

    def _create_cached_nodes(self, graph, pbar):
        cached_nodes = []

        for node in graph.nodes:
            index = len(cached_nodes)
            cached_node = CachedNode(node.type, node.id, node.data, index)
            cached_nodes.append(cached_node)

            pbar.update()

        for edge in graph.edges:
            src = cached_nodes[edge.src]
            dst = cached_nodes[edge.dst]
            relation = edge.relation
            src.add_related_node(dst, relation)

            pbar.update()

        return cached_nodes

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
