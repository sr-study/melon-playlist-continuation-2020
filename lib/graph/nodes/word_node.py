import enum
from ..core import Node


class WordNode(Node):
    class Relation(Node.Relation):
        ALBUM = Node.Relation.auto()
        ARTIST = Node.Relation.auto()
        PLAYLIST = Node.Relation.auto()
        TAG = Node.Relation.auto()

    __slots__ = ['name']

    def __init__(self, id, name):
        super().__init__(id)
        self.name = name
