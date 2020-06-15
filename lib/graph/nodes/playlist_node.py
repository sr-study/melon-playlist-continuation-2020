import enum
from ..core import Node


class PlaylistNode(Node):
    class Relation(Node.Relation):
        TAG = enum.auto()
        SONG = enum.auto()

    __slots__ = ['_id', '_name', '_like_count', '_update_date']

    def __init__(self, graph, id, name, like_count, update_date):
        super().__init__(graph)
        self._id = id
        self._name = name
        self._like_count = like_count
        self._update_date = update_date

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def like_count(self):
        return self._like_count

    @property
    def update_date(self):
        return self._update_date
