import enum
from ..core import Node


class GenreNode(Node):
    class Relation(Node.Relation):
        SONG = Node.Relation.auto()

    __slots__ = ['name']

    def __init__(self, id, name):
        super().__init__(id)
        self.name = name