from collections import Counter
from tqdm import tqdm
from lib.graph import SongNode
from lib.graph import TagNode
from ..utils import convert_to_ids
from ..utils import get_most_common_keys
from ..utils import OrderedSet
from .base import BaseModel


class MostPopular(BaseModel):
    def __init__(self, cached_graph, max_songs, max_tags):
        self._graph = cached_graph
        self._max_songs = max_songs
        self._max_tags = max_tags
        self._most_popular_songs = []
        self._most_popular_tags = []

    def fit(self, playlists):
        song_counts = Counter()
        tag_counts = Counter()

        for playlist in tqdm(playlists, "Fitting MostPopular model"):
            songs = self._graph.get_nodes(
                SongNode, playlist['songs'], ignore_none=True)
            tags = self._graph.get_nodes(
                TagNode, playlist['tags'], ignore_none=True)

            for song in songs:
                song_counts[song] += 1
            for tag in tags:
                tag_counts[tag] += 1

        most_popular_songs = get_most_common_keys(song_counts, self._max_songs)
        most_popular_tags = get_most_common_keys(tag_counts, self._max_tags)

        self._most_popular_songs = convert_to_ids(most_popular_songs)
        self._most_popular_tags = convert_to_ids(most_popular_tags)

        return self

    def predict(self, question):
        return {
            'id': question['id'],
            'songs': self._most_popular_songs,
            'tags': self._most_popular_tags,
        }
