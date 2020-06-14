import enum
from ..core import Node


class GenreNode(Node):
    class EdgeType(Node.EdgeType):
        SONG = enum.auto()

    __slots__ = ['_id', '_name']

    def __init__(self, graph, id, name):
        super().__init__(graph)
        self._id = id
        self._name = name

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name