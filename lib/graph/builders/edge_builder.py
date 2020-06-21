from tqdm import tqdm
from ..core import Graph
from ..core import Edge
from ..nodes import AlbumNode
from ..nodes import ArtistNode
from ..nodes import GenreNode
from ..nodes import PlaylistNode
from ..nodes import SongNode
from ..nodes import TagNode
from .node_manager import NodeManager
from .edge_manager import EdgeManager


class EdgeBuilder:
    def __init__(self, nodes):
        self._nodes = NodeManager(nodes)

    def build(self, songs, genres, playlists):
        edges = EdgeManager()

        total_iters = len(songs) + len(genres) + len(playlists)
        with tqdm(desc="Building edges", total=total_iters) as pbar:
            self._parse_genres(edges, genres, pbar)
            self._parse_songs(edges, songs, pbar)
            self._parse_playlists(edges, playlists, pbar)

        return edges.to_list()

    def _parse_genres(self, edges, genres, pbar):
        for _key, _value in genres.items():
            pbar.update()

    def _parse_songs(self, edges, songs, pbar):
        nodes = self._nodes

        for song in songs:
            song_node = nodes.get(SongNode, song['id'])

            artists = zip(song['artist_id_basket'], song['artist_name_basket'])
            for artist_id, _artist_name in artists:
                artist_node = nodes.get(ArtistNode, artist_id)
                edges.add(Edge(
                    src=song_node,
                    dst=artist_node,
                    relation=SongNode.Relation.ARTIST,
                ))
                edges.add(Edge(
                    src=artist_node,
                    dst=song_node,
                    relation=ArtistNode.Relation.SONG,
                ))

            album_node = nodes.get(AlbumNode, song['album_id'])
            edges.add(Edge(
                src=song_node,
                dst=album_node,
                relation=SongNode.Relation.ALBUM,
            ))
            edges.add(Edge(
                src=album_node,
                dst=song_node,
                relation=AlbumNode.Relation.SONG,
            ))

            for genre_id in song['song_gn_gnr_basket']:
                genre_node = nodes.get(GenreNode, genre_id)
                edges.add(Edge(
                    src=song_node,
                    dst=genre_node,
                    relation=SongNode.Relation.GENRE,
                ))
                edges.add(Edge(
                    src=genre_node,
                    dst=song_node,
                    relation=GenreNode.Relation.SONG,
                ))

            for genre_id in song['song_gn_dtl_gnr_basket']:
                genre_node = nodes.get(GenreNode, genre_id)
                edges.add(Edge(
                    src=song_node,
                    dst=genre_node,
                    relation=SongNode.Relation.GENRE,
                ))
                edges.add(Edge(
                    src=genre_node,
                    dst=song_node,
                    relation=GenreNode.Relation.SONG,
                ))

            pbar.update()

    def _parse_playlists(self, edges, playlists, pbar):
        nodes = self._nodes

        for playlist in playlists:
            playlist_node = nodes.get(PlaylistNode, playlist['id'])

            for tag in playlist['tags']:
                tag_node = nodes.get(TagNode, tag)
                edges.add(Edge(
                    src=playlist_node,
                    dst=tag_node,
                    relation=PlaylistNode.Relation.TAG,
                ))
                edges.add(Edge(
                    src=tag_node,
                    dst=playlist_node,
                    relation=TagNode.Relation.PLAYLIST,
                ))

            for song in playlist['songs']:
                song_node = nodes.get(SongNode, song)
                edges.add(Edge(
                    src=playlist_node,
                    dst=song_node,
                    relation=PlaylistNode.Relation.SONG,
                ))
                edges.add(Edge(
                    src=song_node,
                    dst=playlist_node,
                    relation=SongNode.Relation.PLAYLIST,
                ))

            pbar.update()
