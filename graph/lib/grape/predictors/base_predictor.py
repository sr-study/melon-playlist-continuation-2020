import abc


class BasePredictor(abc.ABC):
    def fit(self, graph):
        pass

    @abc.abstractmethod
    def predict(self, question, params):
        return {
            'id': question['id'],
            'songs': [],
            'tags': [],
        }
