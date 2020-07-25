from ..graph import Graph


class CachedGraph(Graph):
    def __init__(self, graph):
        super().__init__()
        self.nodes = graph.nodes
        self.edges = graph.edges
