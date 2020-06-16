from tqdm import tqdm
from collections import defaultdict
from .cached_graph import CachedGraph
from lib.graph import SongNode, TagNode


class Grape:
    def __init__(self, graph, n_recommended_songs, n_recommended_tags):
        self._initialize(graph, n_recommended_songs, n_recommended_tags)

    def _initialize(self, graph, n_recommended_songs, n_recommended_tags):
        self._graph = CachedGraph(graph)
        self.n_recommended_songs = n_recommended_songs
        self.n_recommended_tags = n_recommended_tags

        self._tag_counts = None
        self._song_counts = None

    def fit(self, playlists):
        self._tag_counts = defaultdict(lambda: 0)
        self._song_counts = defaultdict(lambda: 0)

        for playlist in tqdm(playlists):
            tags = [self._graph.get_node(TagNode, id)
                    for id in playlist['tags'] if self._graph.has_node(TagNode, id)]
            songs = [self._graph.get_node(SongNode, id)
                     for id in playlist['songs'] if self._graph.has_node(SongNode, id)]

            for tag in tags:
                self._tag_counts[tag] += 1
            for song in songs:
                self._song_counts[song] += 1

        return self

    def predict(self, questions):
        answers = []
        for question in tqdm(questions):
            answer = self._predict(question)
            answers.append(answer)

        return answers

    def _predict(self, question):
        question_id = question['id']
        tags = question['tags']
        songs = question['songs']
        title = question['plylst_title']
        like_count = question['like_cnt']
        update_date = question['updt_date']

        predicted_songs = self._predict_songs()
        predicted_tags = self._predict_tags()

        return {
            'id': question_id,
            'songs': predicted_songs,
            'tags': predicted_tags
        }

    def _predict_songs(self):
        return [i for i in range(self.n_recommended_songs)]

    def _predict_tags(self):
        return [str(i) for i in range(self.n_recommended_tags)]
