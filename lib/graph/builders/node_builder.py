from tqdm import tqdm
from ..core import Graph
from ..nodes import AlbumNode
from ..nodes import ArtistNode
from ..nodes import GenreNode
from ..nodes import PlaylistNode
from ..nodes import SongNode
from ..nodes import TagNode
from ..nodes import WordNode
from ..utils import get_words
from .node_manager import NodeManager


class NodeBuilder:
    def build(self, songs, genres, playlists):
        nodes = NodeManager()

        total_iters = len(songs) + len(genres) + len(playlists)
        with tqdm(desc="Building nodes", total=total_iters) as pbar:
            self._parse_genres(nodes, genres, pbar)
            self._parse_songs(nodes, songs, pbar)
            self._parse_playlists(nodes, playlists, pbar)

        return nodes.to_list()

    def _parse_genres(self, nodes, genres, pbar):
        for key, value in genres.items():
            nodes.add(GenreNode(key, value))

    def _parse_songs(self, nodes, songs, pbar):
        for song in songs:
            nodes.add(SongNode(
                id=song['id'],
                name=song['song_name'],
                issue_date=song['issue_date'],
            ))

            artists = zip(song['artist_id_basket'], song['artist_name_basket'])
            for artist_id, artist_name in artists:
                nodes.add(ArtistNode(
                    id=artist_id,
                    name=artist_name,
                ))

            nodes.add(AlbumNode(
                id=song['album_id'],
                name=song['album_name'],
            ))

            for genre_id in song['song_gn_gnr_basket']:
                if nodes.has(GenreNode, genre_id):
                    continue

                nodes.add(GenreNode(
                    id=genre_id,
                    name=None,
                ))

            for genre_id in song['song_gn_dtl_gnr_basket']:
                if nodes.has(GenreNode, genre_id):
                    continue

                nodes.add(GenreNode(
                    id=genre_id,
                    name=None,
                ))

            pbar.update()

    def _parse_playlists(self, nodes, playlists, pbar):
        for playlist in playlists:
            nodes.add(PlaylistNode(
                id=playlist['id'],
                name=playlist['plylst_title'],
                like_count=playlist['like_cnt'],
                update_date=playlist['updt_date'],
            ))

            for tag in playlist['tags']:
                nodes.add(TagNode(
                    id=tag,
                    name=tag,
                ))

                for word in get_words(tag):
                    nodes.add(WordNode(
                        id=word,
                        name=word,
                    ))

            for word in get_words(playlist['plylst_title']):
                nodes.add(WordNode(
                    id=word,
                    name=word,
                ))

            pbar.update()

    def _add_node(self, nodes, node):
        key = (node.__class__, node.id)
        if key in nodes:
            nodes[key] = node
