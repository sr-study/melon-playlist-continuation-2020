import enum
from ..core import Node


class ArtistNode(Node):
    class Relation(Node.Relation):
        SONG = enum.auto()

    __slots__ = ['name']

    def __init__(self, id, name):
        super().__init__(id)
        self.name = name
