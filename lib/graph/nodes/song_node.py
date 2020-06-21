import enum
from ..core import Node


class SongNode(Node):
    class Relation(Node.Relation):
        ARTIST = Node.Relation.auto()
        ALBUM = Node.Relation.auto()
        GENRE = Node.Relation.auto()
        DETAILED_GENRE = Node.Relation.auto()
        PLAYLIST = Node.Relation.auto()

    __slots__ = ['name', 'issue_date']

    def __init__(self, id, name, issue_date):
        super().__init__(id)
        self.name = name
        self.issue_date = issue_date
