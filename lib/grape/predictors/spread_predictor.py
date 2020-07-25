import math
import random
from .base_predictor import BasePredictor
from .utils import remove_seen
from ..collections import ScoreMap
from ..melon_graph import MelonGraph
from ..utils import get_words


class SpreadPredictor(BasePredictor):
    def __init__(self):
        self.graph = None

    def fit(self, graph):
        self.graph = graph

    def predict(self, question, params):
        rand = random.Random(0)

        params.setdefault('song_relation_weight', None)
        params.setdefault('tag_relation_weight', None)
        if params['song_relation_weight'] and params['tag_relation_weight']:
            song_nodes, _ = self._predict_songs_and_tags(
                question,
                params['song_relation_weight'],
                params['max_depth'],
                rand,
            )
            _, tag_nodes = self._predict_songs_and_tags(
                question,
                params['tag_relation_weight'],
                params['max_depth'],
                rand,
            )
        else:
            song_nodes, tag_nodes = self._predict_songs_and_tags(
                question,
                params['relation_weight'],
                params['max_depth'],
                rand,
            )

        songs = [node.id for node in song_nodes]
        tags = [node.id for node in tag_nodes]
        songs = remove_seen(songs, question['songs'], params['max_songs'])
        tags = remove_seen(tags, question['tags'], params['max_tags'])

        return {
            'id': question['id'],
            'songs': songs,
            'tags': tags,
        }

    def _predict_songs_and_tags(self, question, relation_weight, max_depth, rand=None):
        update_date = question['updt_date']

        song_nodes = self.graph.get_nodes(
            MelonGraph.NodeType.SONG, question['songs'])
        tag_nodes = self.graph.get_nodes(
            MelonGraph.NodeType.TAG, question['tags'])
        word_nodes = self.graph.get_nodes(
            MelonGraph.NodeType.WORD, get_words(question['plylst_title']))

        scores = ScoreMap(int)
        weights = ScoreMap(int)
        weights = weights.increase(song_nodes, 1, True)
        weights = weights.increase(tag_nodes, 1, True)
        weights = weights.increase(word_nodes, 1, True)

        for depth in range(max_depth):
            weights = self._move_once_weight(weights, relation_weight)
            scores.add(weights, True)
            # weights = self._prune_weights_top(weights, 20)
            # weights = self._prune_weights_random(weights, depth, rand)
            weights = self._prune_weights_dynamic(weights, depth)

        song_scores = scores.filter(
            lambda k, v: k.type == MelonGraph.NodeType.SONG)
        song_scores = self._filter_by_issue_date(song_scores, update_date)
        top_song_nodes = list(song_scores.top_keys())

        tag_scores = scores.filter(
            lambda k, v: k.type == MelonGraph.NodeType.TAG)
        top_tag_nodes = list(tag_scores.top_keys())

        return top_song_nodes, top_tag_nodes

    def _move_once_weight(self, weights, relation_weight):
        next_weights = ScoreMap(int)
        for node, weight in weights.items():
            for relation, next_nodes in node.related_nodes.items():
                w = relation_weight[relation]
                if w == 0:
                    continue
                for next_node in next_nodes:
                    next_weights[next_node] += weight * w

        return next_weights

    def _prune_weights_top(self, weights, n):
        return ScoreMap(int, dict(weights.top(n)))

    def _prune_weights_random(self, weights, depth, rand):
        next_weights = ScoreMap(int)
        if len(weights) <= 0:
            return next_weights
        log_weights = weights.map(lambda k, v: math.log2(v + 4) - math.log2(4))
        max_w = max(log_weights.values())
        for node, weight in log_weights.items():
            probability = (weight / max_w) * (1 / (depth + 1))
            if rand.random() <= probability:
                next_weights[node] = weight
        next_weights = ScoreMap(
            int, dict(next_weights.top(20 * ((depth + 1) ** 2))))
        return next_weights

    def _prune_weights_dynamic(self, weights, depth):
        def __find_ratio_index(weights, r):
            n = len(weights)
            if n == 0:
                return 0
            max_v = max(weights.values())
            min_v = min(weights.values())
            if max_v == min_v:
                return n
            i = 0
            for _, v in dict(weights.top()).items():
                pos_ratio = ((max_v - v) / (max_v - min_v))
                if pos_ratio > r:
                    return i
                i += 1

            return n

        n = __find_ratio_index(weights, 0.65)
        if depth % 2 == 0:
            n = 20 + 20 * (depth // 2)
        else:
            n = min(max(n, 3), 25)
        next_weights = ScoreMap(int, dict(weights.top(n)))
        return next_weights

    def _filter_by_issue_date(self, song_scores, update_date):
        update_date = f"{update_date[0:4]}{update_date[5:7]}{update_date[8:10]}"

        def __filter_func(node, score):
            issue_date = node.data['issue_date']
            if issue_date[6:8] != '00':
                return issue_date[:8] <= update_date[:8]
            elif issue_date[4:6] != '00':
                return issue_date[:6] <= update_date[:6]
            elif issue_date[0:4] != '00':
                return issue_date[:4] <= update_date[:4]
            return True

        return song_scores.filter(__filter_func)
