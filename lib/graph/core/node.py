import enum


class Node:
    class Relation(enum.Enum):
        pass

    __slots__ = ['id']

    def __init__(self, id):
        self.id = id
