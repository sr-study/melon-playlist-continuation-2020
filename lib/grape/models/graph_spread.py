import math
import random
from tqdm import tqdm
from lib.graph import CachedGraph
from lib.graph import AlbumNode
from lib.graph import ArtistNode
from lib.graph import GenreNode
from lib.graph import MonthNode
from lib.graph import PlaylistNode
from lib.graph import SongNode
from lib.graph import TagNode
from lib.graph import WordNode
from lib.graph import YearNode
from lib.graph.utils import get_words
from .base import BaseModel
from ..utils import merge_unique_lists
from ..utils import convert_to_ids
from ..utils import get_most_common_keys
from ..utils import remove_seen
from ..utils import OrderedSet
from ..utils import ScoreMap


DEBUG = False
# DEBUG = True


class GraphSpread(BaseModel):
    def __init__(self, cached_graph, max_songs, max_tags):
        self._graph = cached_graph
        self._max_songs = max_songs
        self._max_tags = max_tags
        self._rand = None

    def predict(self, question):
        question_id = question['id']
        songs = question['songs']
        tags = question['tags']
        title = question['plylst_title']
        # like_count = question['like_cnt']
        update_date = question['updt_date']

        self._rand = random.Random(0)

        predicted_songs, predicted_tags = self._predict_songs_and_tags(
            songs=songs,
            tags=tags,
            title=title,
            update_date=update_date,
        )

        filtered_songs = remove_seen(
            predicted_songs[:self._max_songs + len(songs)],
            songs)[:self._max_songs]
        filtered_tags = remove_seen(
            predicted_tags[:self._max_tags + len(tags)],
            tags)[:self._max_tags]

        return {
            'id': question_id,
            'songs': filtered_songs,
            'tags': filtered_tags,
        }

    def _predict_songs_and_tags(self, songs, tags, title, update_date):
        song_nodes = self._graph.get_nodes(SongNode, songs)
        tag_nodes = self._graph.get_nodes(TagNode, tags)
        word_nodes = self._graph.get_nodes(WordNode, get_words(title))

        relation_weights = _get_relation_weight()

        scores = ScoreMap(int)
        weights = ScoreMap(int)
        weights = weights.increase(song_nodes, 1, True)
        weights = weights.increase(tag_nodes, 1, True)
        weights = weights.increase(word_nodes, 1, True)

        for depth in range(8):
            # if DEBUG:
            #     print(f'=== current weights ({len(weights)}) ===')
            #     print_weights(weights)
            #     print()

            weights = _move_once_weight(weights, relation_weights)

            if DEBUG:
                print(f'=== moved weights ({len(weights)}) ===')
                print_weights(weights)
                print()

            if DEBUG:
                print(f'=== moved weights histogram ({len(weights)}) ===')
                import matplotlib.pyplot as plt
                print_answer_counts(weights)
                plt.hist(weights.values())
                plt.show()

            scores.add(weights, True)
            weights = _prune_weights(weights, depth, self._rand)
            # weights = ScoreMap(int, dict(weights.top(20)))

        song_scores = scores.filter(lambda k, v: k.node_class == SongNode)
        song_scores = _filter_by_issue_date(song_scores, update_date)
        top_song_ids = convert_to_ids(song_scores.top_keys())

        tag_scores = scores.filter(lambda k, v: k.node_class == TagNode)
        top_tag_ids = convert_to_ids(tag_scores.top_keys())

        return top_song_ids, top_tag_ids


def _move_once_weight(weights, relation_weight):
    next_weights = ScoreMap(int)
    for node, weight in weights.items():
        for relation, w in relation_weight.items():
            if w == 0:
                continue
            for next_node in node.get_related_nodes(relation):
                next_weights[next_node] += weight * w

    return next_weights


def _prune_weights(weights, depth, rand):
    n = _find_ratio_index(weights, 0.65)
    if depth % 2 == 0:
        n = 20 + 20 * (depth // 2)
    else:
        n = min(max(n, 3), 25)
    next_weights = ScoreMap(int, dict(weights.top(n)))
    return next_weights


def _prune_weights_randomly(weights, depth, rand):
    next_weights = ScoreMap(int)
    if len(weights) <= 0:
        return next_weights
    log_weights = weights.map(lambda k, v: math.log2(v + 4) - math.log2(4))
    max_w = max(log_weights.values())
    for node, weight in log_weights.items():
        probability = (weight / max_w) * (1 / (depth + 1))
        if rand.random() <= probability:
            next_weights[node] = weight
    next_weights = ScoreMap(int, dict(next_weights.top(20 * ((depth + 1) ** 2))))
    return next_weights


def _find_ratio_index(weights, r):
    n = len(weights)
    if n == 0:
        return 0
    max_v = max(weights.values())
    min_v = min(weights.values())
    if max_v == min_v:
        return n
    i = 0
    for k, v in dict(weights.top()).items():
        pos_ratio = ((max_v - v) / (max_v - min_v))
        if pos_ratio > r:
            return i
        i += 1

    return n


def _get_relation_weight():
    c = 0.01
    return {
        AlbumNode.Relation.SONG: c * 1,
        AlbumNode.Relation.WORD: c * 0,
        ArtistNode.Relation.SONG: c * 1,
        ArtistNode.Relation.WORD: c * 0,
        GenreNode.Relation.SONG: c * 1,
        MonthNode.Relation.SONG: c * 0,
        PlaylistNode.Relation.SONG: c * 1,
        PlaylistNode.Relation.TAG: c * 2.5,
        PlaylistNode.Relation.WORD: c * 2.5,
        SongNode.Relation.ALBUM: c * 1.5,
        SongNode.Relation.ARTIST: c * 1.5,
        SongNode.Relation.DETAILED_GENRE: c * 0,
        SongNode.Relation.GENRE: c * 0,
        SongNode.Relation.PLAYLIST: c * 0.75,
        SongNode.Relation.MONTH: c * 0,
        SongNode.Relation.YEAR: c * 0,
        TagNode.Relation.PLAYLIST: c * 1,
        TagNode.Relation.WORD: c * 1,
        WordNode.Relation.ALBUM: c * 0,
        WordNode.Relation.ARTIST: c * 0,
        WordNode.Relation.PLAYLIST: c * 1,
        WordNode.Relation.TAG: c * 0.1,
        YearNode.Relation.SONG: c * 0,
        (SongNode.Relation.ARTIST, SongNode.Relation.GENRE): c * 0,
        (SongNode.Relation.ARTIST, SongNode.Relation.DETAILED_GENRE): c * 1.5,
        (ArtistNode.Relation.SONG, GenreNode.Relation.SONG): c * 1,
    }


def _filter_by_issue_date(song_scores, update_date):
    update_date = f"{update_date[0:4]}{update_date[5:7]}{update_date[8:10]}"
    return song_scores.filter(
        lambda k, v:
        k.issue_date[:8] <= update_date[:8] if k.issue_date[6:8] != "00" else
        k.issue_date[:6] <= update_date[:6] if k.issue_date[4:6] != "00" else
        k.issue_date[:4] <= update_date[:4] if k.issue_date[0:4] != "0000" else
        True
    )


def print_weights(weights):
    n = 30
    i = 0
    for k, v in dict(weights.top(n + 1)).items():
        if i < n:
            i += 1
        else:
            print("...")
            break

        if type(k.node_class) is tuple:
            print(f"union: {v}")
        else:
            print(f"{k.node_class.__name__}({k.id}): {v}")


def print_answer_counts(weights):
    answer = {'tags': ['피아노', '뉴에이지', '재즈'], 'id': 20353, 'plylst_title': '따뜻한 봄날의 달달한 피아노 뮤직', 'songs': [238465, 129962, 18663, 409769, 184162, 138251, 573337, 288942, 434503, 175027, 1238, 670743, 279741, 87876, 86289], 'like_cnt': 10, 'updt_date': '2016-05-24 10:10:32.000'}
    # answer = {'tags': ['락발라드', '기분전환', 'Soft_Rock', '락음악', '감성락'], 'id': 89500, 'plylst_title': '몽롱한 감성락! 시끄러운 락이 아닌, 락 발라드! 명곡이 쏟아진다!!', 'songs': [135215, 40820, 112069, 320698, 101972, 69080, 43428, 600975, 427580, 19127, 448887, 260302, 567437, 618720, 705979, 634998, 312626, 78050, 32120, 227312, 230610, 543292], 'like_cnt': 15, 'updt_date': '2020-03-30 18:39:14.000'}

    n_total = len(weights)
    n_songs = 0
    n_tags = 0
    n_answer_songs = 0
    n_answer_tags = 0
    max_v = max(weights.values())
    min_v = min(weights.values())
    i = 0
    for k, v in dict(weights.top()).items():
        if k.node_class is SongNode:
            n_songs += 1
            if k.id in answer['songs']:
                n_answer_songs += 1

                top_percents = (i / n_total) * 100
                pos_percents = ((max_v - v) / (max_v - min_v)) * 100
                print(f"{k.node_class.__name__}({k.id}): {v} ({i}, 상위 {top_percents:.3f}%, 위치 {pos_percents:.3f}% )")
        elif k.node_class is TagNode:
            n_tags += 1
            if k.id in answer['tags']:
                n_answer_tags += 1

                top_percents = (i / n_total) * 100
                pos_percents = ((max_v - v) / (max_v - min_v)) * 100
                print(f"{k.node_class.__name__}({k.id}): {v} ({i}, 상위 {top_percents:.3f}%, 위치 {pos_percents:.3f}% )")
        i += 1

    answer_songs_ratio = (n_answer_songs / n_songs) * 100 if n_songs > 0 else 0
    answer_tags_ratio = (n_answer_tags / n_tags) * 100 if n_tags > 0 else 0

    print(f"max: {max(weights.values())}")
    print(f"min: {min(weights.values())}")
    print(f"total: {n_total}")
    print(f"songs: {n_answer_songs} ({answer_songs_ratio}%)")
    print(f"tags: {n_answer_tags} ({answer_tags_ratio}%)")
