import enum
from ..core import Node


class SongNode(Node):
    class Relation(Node.Relation):
        ARTIST = enum.auto()
        ALBUM = enum.auto()
        GENRE = enum.auto()
        DETAILED_GENRE = enum.auto()
        PLAYLIST = enum.auto()

    __slots__ = ['name', 'issue_date']

    def __init__(self, id, name, issue_date):
        super().__init__(id)
        self.name = name
        self.issue_date = issue_date
