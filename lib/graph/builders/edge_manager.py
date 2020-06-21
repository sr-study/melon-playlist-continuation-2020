class EdgeManager:
    def __init__(self, edges=None):
        self._edges = {}
        if edges:
            self.add_all(edges)

    def has(self, src, dst, relation):
        return (src.id, dst.id, relation) in self._edges

    def get(self, src, dst, relation):
        return self._edges[src.id, dst.id, relation]

    def add(self, edge):
        if not self.has(edge.src, edge.dst, edge.relation):
            self._edges[edge.src.id, edge.dst.id, edge.relation] = edge

    def add_all(self, _edges):
        for edge in _edges:
            self.add(edge)

    def to_list(self):
        return list(self._edges.values())
