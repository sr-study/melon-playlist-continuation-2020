from ..core import Graph
from .node_builder import NodeBuilder
from .edge_builder import EdgeBuilder


class GraphBuilder:
    def build(self, song_meta, genre_gn_all, playlists):
        nodes = NodeBuilder().build(song_meta, genre_gn_all, playlists)
        edges = EdgeBuilder(nodes).build(song_meta, genre_gn_all, playlists)

        graph = self._build_graph(nodes, edges)
        return graph

    def _build_graph(self, nodes, edges):
        graph = Graph()
        graph.add_nodes(nodes)
        graph.add_edges(edges)
        return graph
