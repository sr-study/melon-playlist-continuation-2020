import json
from ..core import Graph
from .func import get_class_key


class GraphEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Graph):
            return self._encode_graph(obj)

        return super().default(obj)

    def _encode_graph(self, graph):
        return {
            '_type': get_class_key(graph.__class__),
            'nodes': [],
            'edges': [],
        }
