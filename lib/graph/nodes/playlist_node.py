import enum
from ..core import Node


class PlaylistNode(Node):
    class Relation(Node.Relation):
        TAG = Node.Relation.auto()
        SONG = Node.Relation.auto()

    __slots__ = ['name', 'like_count', 'update_date']

    def __init__(self, id, name, like_count, update_date):
        super().__init__(id)
        self.name = name
        self.like_count = like_count
        self.update_date = update_date
