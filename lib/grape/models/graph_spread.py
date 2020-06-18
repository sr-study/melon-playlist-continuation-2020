from tqdm import tqdm
from lib.graph import CachedGraph
from lib.graph import SongNode
from lib.graph import TagNode
from lib.graph import PlaylistNode
from .base import BaseModel
from ..utils import merge_unique_lists
from ..utils import convert_to_ids
from ..utils import get_most_common_keys
from ..utils import OrderedSet
from ..utils import ScoreMap


class GraphSpread(BaseModel):
    def __init__(self, cached_graph, max_songs, max_tags):
        self._graph = cached_graph
        self._max_songs = max_songs
        self._max_tags = max_tags

    def predict(self, question):
        question_id = question['id']
        songs = question['songs']
        tags = question['tags']
        # title = question['plylst_title']
        # like_count = question['like_cnt']
        # update_date = question['updt_date']

        answer_songs = self._predict_songs(
            songs=songs,
            tags=tags,
        )
        answer_tags = self._predict_tags(
            songs=songs,
            tags=tags,
        )

        return {
            'id': question_id,
            'songs': answer_songs,
            'tags': answer_tags,
        }

    def _predict_songs(self, songs, tags):
        if not tags and not songs:
            return []

        song_nodes = self._graph.get_nodes(SongNode, songs, ignore_none=True)
        tag_nodes = self._graph.get_nodes(TagNode, tags, ignore_none=True)

        scores = ScoreMap(int)
        weights = ScoreMap(int)
        weights.increase(song_nodes, 1, modify=True)
        weights.increase(tag_nodes, 1, modify=True)

        weights = ScoreMap(int, dict(_move_once(weights).top(20)))
        weights = _move_once(weights)
        scores.add(weights, modify=True)

        song_scores = scores.filter(lambda k, v: k.get_class() == SongNode)
        predicted_songs = OrderedSet(song_nodes) | song_scores.top_keys()

        return convert_to_ids(predicted_songs)[:self._max_songs]

    def _predict_tags(self, songs, tags):
        if not tags and not songs:
            return []

        song_nodes = self._graph.get_nodes(SongNode, songs, ignore_none=True)
        tag_nodes = self._graph.get_nodes(TagNode, tags, ignore_none=True)

        scores = ScoreMap(int)
        weights = ScoreMap(int)
        weights.increase(song_nodes, 1, modify=True)
        weights.increase(tag_nodes, 1, modify=True)

        weights = ScoreMap(int, dict(_move_once(weights).top(20)))
        weights = _move_once(weights)
        scores.add(weights, modify=True)

        tag_scores = scores.filter(lambda k, v: k.get_class() == TagNode)
        predicted_tags = OrderedSet(tag_nodes) | tag_scores.top_keys()

        return convert_to_ids(predicted_tags)[:self._max_tags]


def _move_once(weights, relations=None):
    next_weights = ScoreMap(int)
    if relations is None:
        for node, weight in weights.items():
            for next_node in node.get_related_nodes():
                next_weights[next_node] += weight
    else:
        for node, weight in weights.items():
            next_nodes = []
            for relation in relations:
                for next_node in node.get_related_nodes(relation):
                    next_nodes.append(next_node)

            for next_node in next_nodes:
                next_weights[next_node] += weight

    return next_weights