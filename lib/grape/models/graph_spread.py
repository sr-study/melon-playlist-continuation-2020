from tqdm import tqdm
from lib.graph import CachedGraph
from lib.graph import AlbumNode
from lib.graph import ArtistNode
from lib.graph import GenreNode
from lib.graph import PlaylistNode
from lib.graph import SongNode
from lib.graph import TagNode
from lib.graph import WordNode
from lib.graph.utils import get_words
from .base import BaseModel
from ..utils import merge_unique_lists
from ..utils import convert_to_ids
from ..utils import get_most_common_keys
from ..utils import remove_seen
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
        title = question['plylst_title']
        # like_count = question['like_cnt']
        update_date = question['updt_date']

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

        for _i in range(8):
            weights = _move_once_weight(weights, relation_weights)
            scores.add(weights, True)
            weights = ScoreMap(int, dict(weights.top(20)))

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


def _get_relation_weight():
    c = 0.01
    return {
        AlbumNode.Relation.SONG: c * 1,
        ArtistNode.Relation.SONG: c * 1,
        GenreNode.Relation.SONG: c * 1,
        PlaylistNode.Relation.SONG: c * 1,
        PlaylistNode.Relation.TAG: c * 2.5,
        PlaylistNode.Relation.WORD: c * 2.5,
        SongNode.Relation.ALBUM: c * 1.5,
        SongNode.Relation.ARTIST: c * 1.5,
        SongNode.Relation.DETAILED_GENRE: c * 0,
        SongNode.Relation.GENRE: c * 0,
        SongNode.Relation.PLAYLIST: c * 0.75,
        TagNode.Relation.PLAYLIST: c * 1,
        TagNode.Relation.WORD: c * 1,
        WordNode.Relation.PLAYLIST: c * 1,
        WordNode.Relation.TAG: c * 0.1,
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
