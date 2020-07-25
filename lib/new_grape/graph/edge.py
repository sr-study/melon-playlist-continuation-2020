class Edge:
    __slots__ = ['src', 'dst', 'relation']

    def __init__(self, src, dst, relation):
        self.src = src
        self.dst = dst
        self.relation = relation

    def state(self):
        return [self.src, self.dst, self.relation]

    @classmethod
    def from_state(cls, state):
        return Edge(*state)
