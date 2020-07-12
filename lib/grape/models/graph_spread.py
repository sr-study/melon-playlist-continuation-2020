from tqdm import tqdm
from lib.graph import CachedGraph
from lib.graph import AlbumNode
from lib.graph import ArtistNode
from lib.graph import GenreNode
from lib.graph import PlaylistNode
from lib.graph import SongNode
from lib.graph import TagNode
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
        # title = question['plylst_title']
        # like_count = question['like_cnt']
        update_date = question['updt_date']

        predicted_songs = self._predict_songs(
            songs=songs,
            tags=tags,
            update_date=update_date,
        )
        predicted_tags = self._predict_tags(
            songs=songs,
            tags=tags,
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

    def _predict_songs(self, songs, tags, update_date):
        if not tags and not songs:
            return []

        song_nodes = self._graph.get_nodes(SongNode, songs)
        tag_nodes = self._graph.get_nodes(TagNode, tags)

        relation_weights = _get_relation_weight_5()

        scores = ScoreMap(int)
        weights = ScoreMap(int)
        weights = weights.increase(song_nodes, 1, True)
        weights = weights.increase(tag_nodes, 1, True)

        for _i in range(8):
            weights = _move_once_weight(weights, relation_weights)
            scores.add(weights, True)
            weights = ScoreMap(int, dict(weights.top(20)))

        song_scores = scores.filter(lambda k, v: k.node_class == SongNode)
        song_scores = _filter_by_issue_date(song_scores, update_date)
        top_song_ids = convert_to_ids(song_scores.top_keys())

        return top_song_ids

    def _predict_tags(self, songs, tags, update_date):
        if not tags and not songs:
            return []

        song_nodes = self._graph.get_nodes(SongNode, songs)
        tag_nodes = self._graph.get_nodes(TagNode, tags)

        relation_weights = _get_relation_weight_1()

        scores = ScoreMap(int)
        weights = ScoreMap(int)
        weights = weights.increase(song_nodes, 1, True)
        weights = weights.increase(tag_nodes, 1, True)

        for _i in range(8):
            weights = _move_once_weight(weights, relation_weights)
            scores.add(weights, True)
            weights = ScoreMap(int, dict(weights.top(20)))

        tag_scores = scores.filter(lambda k, v: k.node_class == TagNode)
        top_tag_ids = convert_to_ids(tag_scores.top_keys())

        return top_tag_ids


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


def _move_once_weight(weights, relation_weight):
    next_weights = ScoreMap(int)
    for node, weight in weights.items():
        for relation, w in relation_weight.items():
            if w == 0:
                continue
            for next_node in node.get_related_nodes(relation):
                next_weights[next_node] += weight * w

    return next_weights


def _get_relation_weight_1():
    c = 0.01
    return {
        AlbumNode.Relation.SONG: c * 1,
        ArtistNode.Relation.SONG: c * 1,
        GenreNode.Relation.SONG: c * 1,
        PlaylistNode.Relation.SONG: c * 1,
        PlaylistNode.Relation.TAG: c * 2,
        SongNode.Relation.ALBUM: c * 0.2,
        SongNode.Relation.ARTIST: c * 0.8,
        SongNode.Relation.DETAILED_GENRE: c * 0,
        SongNode.Relation.GENRE: c * 0,
        SongNode.Relation.PLAYLIST: c * 0.75,
        TagNode.Relation.PLAYLIST: c * 6,
        (SongNode.Relation.ARTIST, SongNode.Relation.GENRE): c * 0,
        (SongNode.Relation.ARTIST, SongNode.Relation.DETAILED_GENRE): c * 0,
        (ArtistNode.Relation.SONG, GenreNode.Relation.SONG): c * 0,
    }


def _get_relation_weight_5():
    c = 0.01
    return {
        AlbumNode.Relation.SONG: c * 1,
        ArtistNode.Relation.SONG: c * 1,
        GenreNode.Relation.SONG: c * 1,
        PlaylistNode.Relation.SONG: c * 1,
        PlaylistNode.Relation.TAG: c * 2.5,
        SongNode.Relation.ALBUM: c * 1.5,
        SongNode.Relation.ARTIST: c * 1.5,
        SongNode.Relation.DETAILED_GENRE: c * 0,
        SongNode.Relation.GENRE: c * 0,
        SongNode.Relation.PLAYLIST: c * 0.75,
        TagNode.Relation.PLAYLIST: c * 1,
        (SongNode.Relation.ARTIST, SongNode.Relation.GENRE): c * 0,
        (SongNode.Relation.ARTIST, SongNode.Relation.DETAILED_GENRE): c * 1.5,
        (ArtistNode.Relation.SONG, GenreNode.Relation.SONG): c * 1,
    }


def _get_all_relations():
    return set([
        AlbumNode.Relation.SONG,
        ArtistNode.Relation.SONG,
        GenreNode.Relation.SONG,
        PlaylistNode.Relation.SONG,
        PlaylistNode.Relation.TAG,
        SongNode.Relation.ALBUM,
        SongNode.Relation.ARTIST,
        SongNode.Relation.DETAILED_GENRE,
        SongNode.Relation.GENRE,
        SongNode.Relation.PLAYLIST,
        TagNode.Relation.PLAYLIST,
        (SongNode.Relation.ARTIST, SongNode.Relation.GENRE),
        (ArtistNode.Relation.SONG, GenreNode.Relation.SONG),
    ])


def _filter_by_issue_date(song_scores, update_date):
    update_date = f"{update_date[0:4]}{update_date[5:7]}{update_date[8:10]}"
    return song_scores.filter(
        lambda k, v:
        k.issue_date[:8] <= update_date[:8] if k.issue_date[6:8] != "00" else
        k.issue_date[:6] <= update_date[:6] if k.issue_date[4:6] != "00" else
        k.issue_date[:4] <= update_date[:4] if k.issue_date[0:4] != "0000" else
        True
    )
