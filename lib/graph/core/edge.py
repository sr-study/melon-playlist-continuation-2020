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

    def __hash__(self):
        return hash((self._src, self._dst, self._relation))

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self._src == other._src and
            self._dst == other._dst and
            self._relation == other._relation
        )
