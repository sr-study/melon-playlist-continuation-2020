import enum
from .element import Element


class Node(Element):
    class Relation(enum.Enum):
        pass

    def __init__(self, graph):
        super().__init__(graph)
