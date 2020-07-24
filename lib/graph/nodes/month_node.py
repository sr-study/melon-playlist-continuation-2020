import enum
from ..core import Node


class MonthNode(Node):
    class Relation(Node.Relation):
        SONG = Node.Relation.auto()

    __slots__ = []

    def __init__(self, id):
        super().__init__(id)
