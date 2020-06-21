import enum


class Node:
    class Relation:
        _auto_id = 0

        @classmethod
        def auto(cls):
            cls._auto_id += 1
            return cls._auto_id

    __slots__ = ['id']

    def __init__(self, id):
        self.id = id
