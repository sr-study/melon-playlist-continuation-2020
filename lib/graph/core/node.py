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
