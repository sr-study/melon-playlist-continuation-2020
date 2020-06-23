from tqdm import tqdm
from lib.graph import CachedGraph
from .models import BaseModel
from .models import GraphSpread
from .models import MostPopular
from .utils import merge_unique_lists
from .utils import remove_seen


class Grape(BaseModel):
    def __init__(self, graph, max_songs, max_tags):
        self._initialize(graph, max_songs, max_tags)

    def _initialize(self, graph, max_songs, max_tags):
        self._graph = CachedGraph(graph)
        self._max_songs = max_songs
        self._max_tags = max_tags
        self._graph_spread = GraphSpread(
            self._graph,
            self._max_songs,
            self._max_tags,
        )
        self._most_popular = MostPopular(
            self._graph,
            self._max_songs,
            self._max_tags,
        )

        _cache_union_nodes(self._graph)

    def fit(self, playlists):
        self._most_popular.fit(playlists)
        return self

    def predict(self, question):
        results = []
        results.append(self._graph_spread.predict(question))
        results.append(self._most_popular.predict(question))

        merged_songs = merge_unique_lists(
            *(result['songs'] for result in results))
        merged_tags = merge_unique_lists(
            *(result['tags'] for result in results))

        filtered_songs = remove_seen(merged_songs, question['songs'])
        filtered_tags = remove_seen(merged_tags, question['tags'])

        answer_songs = filtered_songs[:self._max_songs]
        answer_tags = filtered_tags[:self._max_tags]

        return {
            'id': question['id'],
            'songs': answer_songs,
            'tags': answer_tags,
        }


def _cache_union_nodes(graph):
    from lib.graph import ArtistNode
    from lib.graph import GenreNode
    from lib.graph import SongNode
    from lib.graph import UnionNode
    from lib.graph import CachedEdge

    for node in tqdm(graph.nodes, "Caching union nodes"):
        if node.node_class == SongNode:
            artists = node.get_related_nodes(SongNode.Relation.ARTIST)
            genres = node.get_related_nodes(SongNode.Relation.GENRE)
            for artist in artists:
                for genre in genres:
                    if graph.has_node((ArtistNode, GenreNode), (artist.id, genre.id)):
                        union = graph.get_node((ArtistNode, GenreNode), (artist.id, genre.id))
                    else:
                        union = UnionNode(len(graph.nodes), [artist, genre])
                        graph.add_node(union)
                    graph.add_edge(CachedEdge(node, union, (SongNode.Relation.ARTIST, SongNode.Relation.GENRE)))
                    graph.add_edge(CachedEdge(union, node, (ArtistNode.Relation.SONG, GenreNode.Relation.SONG)))
