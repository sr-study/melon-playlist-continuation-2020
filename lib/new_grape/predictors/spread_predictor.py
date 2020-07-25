from .base_predictor import BasePredictor


class SpreadPredictor(BasePredictor):
    def __init__(self):
        self.graph = None

    def fit(self, graph):
        self.graph = graph

    def predict(self, question, params):
        return {
            'id': question['id'],
            'songs': [],
            'tags': [],
        }
