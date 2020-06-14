import sys
from ..core import Edge, Element, Graph, Node
from ..nodes import AlbumNode, ArtistNode, GenreNode, PlaylistNode, SongNode, TagNode


def get_class_key(cls):
    return cls.__qualname__


def get_class_by_key(key):
    cursor = sys.modules[__name__]
    for name in key.split('.'):
        cursor = getattr(cursor, name)
    return cursor
