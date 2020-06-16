from tqdm import tqdm
from .cached_graph import CachedGraph
from lib.graph import SongNode, TagNode
from arena_util import remove_seen


class Grape:
    def __init__(self, graph):
        self._initialize(graph)

    def _initialize(self, graph):
        self._graph = CachedGraph(graph)

    def predict(self, questions):
        answers = []
        for question in tqdm(questions):
            question_id = question['id']
            input_tags = question['tags']
            input_songs = question['songs']

            for tid in input_tags:
                if not self._graph.has_node(TagNode, tid):
                    continue
                tag = self._graph.get_node(TagNode, tid)

            for sid in input_songs:
                song = self._graph.get_node(SongNode, sid)

            predicted_tags = list(set(input_tags + [f"{i}" for i in range(10)]))[:10]
            predicted_songs = list(set(input_songs + [i for i in range(100)]))[:100]

            answers.append({
                'id': question_id,
                "songs": predicted_songs,
                "tags": predicted_tags
            })

        return answers
