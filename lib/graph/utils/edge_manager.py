from collections import defaultdict
from ..core import Edge


class EdgeManager:
    def __init__(self, graph):
        def nested_dict():
            return defaultdict(nested_dict)

        self._graph = graph
        self._edges = nested_dict()

    def get_or_create(self, src, dst, relation):
        edge = self._edges[src][dst][relation]
        if edge:
            return edge
        else:
            return self._create(src, dst, relation)

    def has(self, src, dst, relation):
        return bool(self._edges[src][dst][relation])

    def get(self, src, dst, relation):
        if not self.has(src, dst, relation):
            raise Exception("Edge not exists")

        return self._edges[src][dst][relation]

    def _create(self, src, dst, relation):
        if self.has(src, dst, relation):
            raise Exception("Node already exists")

        edge = self._graph.create_edge(src, dst, relation)
        self._edges[src][dst][relation] = edge
        return edge
