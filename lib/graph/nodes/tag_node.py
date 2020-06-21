import enum
from ..core import Node


class TagNode(Node):
    class Relation:
        PLAYLIST = 1

    __slots__ = ['name']

    def __init__(self, id, name):
        super().__init__(id)
        self.name = name
