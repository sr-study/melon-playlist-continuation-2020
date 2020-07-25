from .base_predictor import BasePredictor
from .utils import merge_uniques


class EnsemblePredictor(BasePredictor):
    def __init__(self):
        self._children = []

    def register(self, predictor):
        self._children.append(predictor)

    def fit(self, graph):
        for predictor in self._children:
            predictor.fit(graph)

    def predict(self, question, params):
        results = []
        for predictor in self._children:
            results.append(predictor.predict(question, params))

        songs_results = [result['songs'] for result in results]
        tags_results = [result['tags'] for result in results]

        merged_songs = merge_uniques(*songs_results)
        merged_tags = merge_uniques(*tags_results)

        return {
            'id': question['id'],
            'songs': merged_songs[:params['max_songs']],
            'tags': merged_tags[:params['max_tags']],
        }
