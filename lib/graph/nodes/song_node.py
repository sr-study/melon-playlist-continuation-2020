import enum
from ..core import Node


class SongNode(Node):
    class Relation(Node.Relation):
        ARTIST = enum.auto()
        ALBUM = enum.auto()
        GENRE = enum.auto()
        DETAILED_GENRE = enum.auto()
        PLAYLIST = enum.auto()

    __slots__ = ['_name', '_issue_date']

    def __init__(self, graph, id, name, issue_date):
        super().__init__(graph, id)
        self._name = name
        self._issue_date = issue_date

    @property
    def name(self):
        return self._name

    @property
    def issue_date(self):
        return self._issue_date
