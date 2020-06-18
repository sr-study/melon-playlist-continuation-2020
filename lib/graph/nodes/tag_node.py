import enum
from ..core import Node


class TagNode(Node):
    class Relation(Node.Relation):
        PLAYLIST = enum.auto()

    __slots__ = ['_name']

    def __init__(self, graph, id, name):
        super().__init__(graph, id)
        self._name = name

    @property
    def name(self):
        return self._name
