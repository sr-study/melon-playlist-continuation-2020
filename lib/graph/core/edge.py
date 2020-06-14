from .element import Element


class Edge(Element):
    __slots__ = ['_owner', '_src', '_dst', '_type']

    def __init__(self, graph, src, dst, edge_type):
        super().__init__(graph)
        self._src = src
        self._dst = dst
        self._type = edge_type
