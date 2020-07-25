from .base_predictor import BasePredictor
from .utils import remove_seen
from ..melon_graph import MelonGraph


class MostPopularPredictor(BasePredictor):
    def __init__(self):
        self.songs = []
        self.tags = []

    def fit(self, graph):
        song_nodes = graph.get_all_nodes(MelonGraph.NodeType.SONG)
        tag_nodes = graph.get_all_nodes(MelonGraph.NodeType.TAG)

        sorted(song_nodes,
               key=lambda node: node.data['indegree'],
               reverse=True)
        sorted(tag_nodes,
               key=lambda node: node.data['indegree'],
               reverse=True)

        self.songs = [node.id for node in song_nodes]
        self.tags = [node.id for node in tag_nodes]

    def predict(self, question, params):
        songs = remove_seen(self.songs, question['songs'], params['max_songs'])
        tags = remove_seen(self.tags, question['tags'], params['max_tags'])

        return {
            'id': question['id'],
            'songs': songs,
            'tags': tags,
        }
