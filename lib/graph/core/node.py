import enum
from .element import Element


class Node(Element):
    class Relation(enum.Enum):
        pass

    __slots__ = ['_id']

    def __init__(self, graph, id):
        super().__init__(graph)
        self._id = id

    @property
    def id(self):
        return self._id

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self._id == other._id
        )
