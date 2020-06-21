class CachedEdge:
    __slots__ = ['src', 'dst', 'relation']

    def __init__(self, src, dst, relation):
        self.src = src
        self.dst = dst
        self.relation = relation
