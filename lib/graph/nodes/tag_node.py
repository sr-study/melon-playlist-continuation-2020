import enum
from ..core import Node


class TagNode(Node):
    class Relation(Node.Relation):
        PLAYLIST = enum.auto()

    __slots__ = ['name']

    def __init__(self, id, name):
        super().__init__(id)
        self.name = name
