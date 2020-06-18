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
