from tqdm import tqdm
from collections import defaultdict
from lib.graph import CachedGraph
from lib.graph import SongNode, TagNode
from .utils import merge_unique_lists


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

        for playlist in tqdm(playlists, "Fitting grape"):
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
        self._most_popular_songs = self._predict_most_popular_songs()
        self._most_popular_tags = self._predict_most_popular_tags()

        answers = []
        for question in tqdm(questions):
            answer = self._predict(question)
            answers.append(answer)

        return answers

    def _predict(self, question):
        question_id = question['id']
        songs = question['songs']
        tags = question['tags']
        title = question['plylst_title']
        like_count = question['like_cnt']
        update_date = question['updt_date']

        predicted_songs = self._predict_songs()
        predicted_tags = self._predict_tags()

        answer_songs = merge_unique_lists(
            songs, predicted_songs)[:self.n_recommended_songs]
        answer_tags = merge_unique_lists(
            tags, predicted_tags)[:self.n_recommended_tags]

        return {
            'id': question_id,
            'songs': answer_songs,
            'tags': answer_tags,
        }

    def _predict_songs(self):
        return self._most_popular_songs

    def _predict_tags(self):
        return self._most_popular_tags

    def _predict_most_popular_songs(self):
        sorted_songs = sorted(
            self._song_counts, key=self._song_counts.get, reverse=True)
        return [song.id for song in sorted_songs][:self.n_recommended_songs]

    def _predict_most_popular_tags(self):
        sorted_tags = sorted(
            self._tag_counts, key=self._tag_counts.get, reverse=True)
        return [tag.id for tag in sorted_tags][:self.n_recommended_tags]
