import copy
import pickle

from ..cached_graph import CachedGraph
from ..melon_graph import MelonGraphBuilder
from ..graph import Graph


class Grape:
    def __init__(self):
        self._graph = None
        self._params = {
            'max_depth': 2,
            'edge_resistance': {},
        }

    def fit(self, songs, genres, playlists):
        graph_builder = MelonGraphBuilder()
        graph = graph_builder.build(songs, genres, playlists)
        self._graph = CachedGraph(graph)

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

    def __call__(self, playlist, params=None):
        if self._graph is None:
            raise Exception("Grape model is not initialized")

        if params is None:
            params = self._params

        return playlist
