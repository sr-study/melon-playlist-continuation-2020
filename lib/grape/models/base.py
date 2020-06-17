import abc
import tqdm


class BaseModel(abc.ABC):
    def predict_all(self, questions):
        answers = []
        for question in tqdm.tqdm(questions):
            answer = self.predict(question)
            answers.append(answer)

        return answers

    @abc.abstractmethod
    def predict(self, question):
        return {
            'id': question['id'],
            'songs': [],
            'tags': [],
        }
