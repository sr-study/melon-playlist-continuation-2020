import enum


class Node:
    class Relation:
        pass

    __slots__ = ['id']

    def __init__(self, id):
        self.id = id
