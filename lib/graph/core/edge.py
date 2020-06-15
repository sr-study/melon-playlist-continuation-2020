from .element import Element


class Edge(Element):
    __slots__ = ['_owner', '_src', '_dst', '_relation']

    def __init__(self, graph, src, dst, relation):
        super().__init__(graph)
        self._src = src
        self._dst = dst
        self._relation = relation

    @property
    def src(self):
        return self._src

    @property
    def dst(self):
        return self._dst

    @property
    def relation(self):
        return self._relation
