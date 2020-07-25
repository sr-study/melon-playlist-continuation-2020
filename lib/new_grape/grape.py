import copy
import pickle

from .cached_graph import CachedGraph
from .melon_graph import MelonGraph
from .melon_graph import MelonGraphBuilder
from .graph import Graph
from .predictors import EnsemblePredictor
from .predictors import MostPopularPredictor
from .predictors import SpreadPredictor


class Grape:
    def __init__(self):
        self._graph = None
        self._params = {
            'max_songs': 100,
            'max_tags': 10,
            'max_depth': 2,
            'relation_scale': {
                MelonGraph.Relation.ALBUM_TO_SONG: 0.01,
                MelonGraph.Relation.ALBUM_TO_WORD: 0,
                MelonGraph.Relation.ARTIST_TO_SONG: 0.01,
                MelonGraph.Relation.ARTIST_TO_WORD: 0,
                MelonGraph.Relation.ARTIST_GENRE_TO_SONG: 0.01,
                MelonGraph.Relation.GENRE_TO_SONG: 0.01,
                MelonGraph.Relation.MONTH_TO_SONG: 0,
                MelonGraph.Relation.PLAYLIST_TO_SONG: 0.01,
                MelonGraph.Relation.PLAYLIST_TO_TAG: 0.025,
                MelonGraph.Relation.PLAYLIST_TO_WORD: 0.025,
                MelonGraph.Relation.SONG_TO_ALBUM: 0.015,
                MelonGraph.Relation.SONG_TO_ARTIST: 0.015,
                MelonGraph.Relation.SONG_TO_ARTIST_DETAILED_GENRE: 0.015,
                MelonGraph.Relation.SONG_TO_ARTIST_GENRE: 0,
                MelonGraph.Relation.SONG_TO_DETAILED_GENRE: 0,
                MelonGraph.Relation.SONG_TO_GENRE: 0,
                MelonGraph.Relation.SONG_TO_MONTH: 0,
                MelonGraph.Relation.SONG_TO_PLAYLIST: 0.0075,
                MelonGraph.Relation.SONG_TO_YEAR: 0,
                MelonGraph.Relation.TAG_TO_PLAYLIST: 0.01,
                MelonGraph.Relation.TAG_TO_WORD: 0.01,
                MelonGraph.Relation.WORD_TO_ALBUM: 0,
                MelonGraph.Relation.WORD_TO_ARTIST: 0,
                MelonGraph.Relation.WORD_TO_PLAYLIST: 0.01,
                MelonGraph.Relation.WORD_TO_TAG: 0.001,
                MelonGraph.Relation.YEAR_TO_SONG: 0,
            },
        }
        self._predictor = EnsemblePredictor()
        self._predictor.register(MostPopularPredictor())
        self._predictor.register(SpreadPredictor())

    def fit(self, songs, genres, playlists):
        graph_builder = MelonGraphBuilder()
        graph = graph_builder.build(songs, genres, playlists)
        self._graph = CachedGraph(graph)
        self._predictor.fit(self._graph)

    def set_params(self, **params):
        self._params.update(params)

    def params(self):
        return copy.deepcopy(self._params)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump((self._graph.state(), self._params), f)

    def load(self, path):
        with open(path, 'rb') as f:
            graph_state, params = pickle.load(f)

        graph = Graph.from_state(graph_state)
        self._graph = CachedGraph(graph)
        self._params = params
        self._predictor.fit(self._graph)

    def __call__(self, playlist, params=None):
        if self._graph is None:
            raise Exception("Grape model is not initialized")

        if params is None:
            params = self._params

        return self._predictor.predict(playlist, params)
