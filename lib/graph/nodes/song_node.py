import enum
from ..core import Node


class SongNode(Node):
    class Relation:
        ARTIST = 1
        ALBUM = 2
        GENRE = 3
        DETAILED_GENRE = 4
        PLAYLIST = 5

    __slots__ = ['name', 'issue_date']

    def __init__(self, id, name, issue_date):
        super().__init__(id)
        self.name = name
        self.issue_date = issue_date
