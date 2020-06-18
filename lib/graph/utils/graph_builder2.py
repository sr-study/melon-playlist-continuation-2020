import multiprocessing as mp
import numpy as np
from tqdm.auto import tqdm
from ..core import Graph
from ..nodes import AlbumNode
from ..nodes import ArtistNode
from ..nodes import GenreNode
from ..nodes import PlaylistNode
from ..nodes import SongNode
from ..nodes import TagNode
from .node_manager import NodeManager
from .edge_manager import EdgeManager


class GraphBuilder:
    def __init__(self, song_meta, genre_gn_all, playlists,
                 jobs=None, processes=None):
        assert (processes is None) or (processes >= 1)
        assert (jobs is None) or (jobs >= 1)

        self._songs = song_meta
        self._genres = genre_gn_all
        self._playlists = playlists

        self._processes = mp.cpu_count() if processes is None else processes
        self._jobs = self._processes if jobs is None else jobs
        self._graph = None
        self._nodes = None
        self._edges = None

    def build(self):
        self._initialize()
        self._build_nodes()
        self._build_edges()

        return self._graph

    def _initialize(self):
        self._graph = Graph()
        self._nodes = {}
        self._edges = {}
        self._chunks = self._prepare_chunks(self._jobs)

    def _prepare_chunks(self, n_chunks):
        song_chunks = np.array_split(self._songs, n_chunks)
        genre_chunks = np.array_split(list(self._genres.items()), n_chunks)
        playlist_chunks = np.array_split(self._playlists, n_chunks)
        return list(zip(song_chunks, genre_chunks, playlist_chunks))

    def _build_nodes(self):
        if self._jobs == 1:
            self._build_nodes_singleprocessing()
        else:
            self._build_nodes_multiprocessing()

    def _build_nodes_singleprocessing(self):
        for chunk in tqdm(self._chunks, "Building nodes"):
            self._nodes.update(self._create_nodes(chunk))

        for node in self._nodes.values():
            self._graph.add_node(node)

    def _build_nodes_multiprocessing(self):
        with mp.Pool(self._processes) as pool:
            for nodes in tqdm(
                    pool.imap_unordered(self._create_nodes, self._chunks),
                    "Building nodes",
                    total=len(self._chunks)):
                self._nodes.update(nodes)

        for node in self._nodes.values():
            self._graph.add_node(node)

    def _create_nodes(self, chunk):
        songs, genres, playlists = chunk
        nodes = {}

        total_length = len(songs) + len(genres) + len(playlists)
        with tqdm(desc="Creating nodes", total=total_length) as pbar:
            
            self._create_genre_nodes(genres, nodes, pbar)
            self._create_song_nodes(songs, nodes, pbar)
            self._create_playlist_nodes(playlists, nodes, pbar)

        return nodes

    def _create_genre_nodes(self, genres, nodes, pbar):
        graph = self._graph

        for key, value in genres:
            # nodes[GenreNode, key] = GenreNode(
            #     graph=graph,
            #     id=key,
            #     name=value,
            # )
            import time
            time.sleep(0.01)

            pbar.update()

    def _create_song_nodes(self, songs, nodes, pbar):
        graph = self._graph

        for song in songs:
            nodes[SongNode, song['id']] = SongNode(
                graph=graph,
                id=song['id'],
                name=song['song_name'],
                issue_date=song['issue_date'],
            )

            nodes[AlbumNode, song['album_id']] = AlbumNode(
                graph=graph,
                id=song['album_id'],
                name=song['album_name'],
            )

            artists = zip(song['artist_id_basket'], song['artist_name_basket'])
            for id_, name in artists:
                nodes[ArtistNode, id_] = ArtistNode(
                    graph=graph,
                    id=id_,
                    name=name,
                )

            for id_ in song['song_gn_gnr_basket']:
                if (GenreNode, id_) not in nodes:
                    nodes[GenreNode, id_] = GenreNode(
                        graph=graph,
                        id=id_,
                        name=None,
                    )

            for id_ in song['song_gn_dtl_gnr_basket']:
                if (GenreNode, id_) not in nodes:
                    nodes[GenreNode, id_] = GenreNode(
                        graph=graph,
                        id=id_,
                        name=None,
                    )

            pbar.update()

    def _create_playlist_nodes(self, playlists, nodes, pbar):
        graph = self._graph

        for playlist in playlists:
            nodes[PlaylistNode, playlist['id']] = PlaylistNode(
                graph=graph,
                id=playlist['id'],
                name=playlist['plylst_title'],
                like_count=playlist['like_cnt'],
                update_date=playlist['updt_date'],
            )

            for tag in playlist['tags']:
                nodes[TagNode, tag] = TagNode(
                    graph=graph,
                    id=tag,
                    name=tag,
                )

            pbar.update()

    def _build_edges(self):
        edges = []
        # with mp.Pool(self._processes) as pool:
        for args in self._chunks:
            edges += self._create_edges(*args)

        for edge in edges:
            self._graph.add_edge(edge)

    def _create_edges(self, songs, genres, playlists):
        return []

    # def _parse_genres(self, genre_gn_all):
    #     for key, value in tqdm(genre_gn_all.items(), "Parsing genres"):
    #         self._genres.get_or_create(id=key, name=value)

    # def _parse_songs(self, song_metas):
    #     for song_meta in tqdm(song_metas, "Parsing songs"):
    #         song = self._songs.get_or_create(
    #             id=song_meta['id'],
    #             name=song_meta['song_name'],
    #             issue_date=song_meta['issue_date'],
    #         )

    #         artists = zip(song_meta['artist_id_basket'],
    #                       song_meta['artist_name_basket'])
    #         for artist_id, artist_name in artists:
    #             artist = self._artists.get_or_create(
    #                 id=artist_id,
    #                 name=artist_name,
    #             )
    #             self._edges.get_or_create(
    #                 song, artist, SongNode.Relation.ARTIST)
    #             self._edges.get_or_create(
    #                 artist, song, ArtistNode.Relation.SONG)

    #         album = self._albums.get_or_create(
    #             id=song_meta['album_id'],
    #             name=song_meta['album_name'],
    #         )
    #         self._edges.get_or_create(song, album, SongNode.Relation.ALBUM)
    #         self._edges.get_or_create(album, song, AlbumNode.Relation.SONG)

    #         for genre_id in song_meta['song_gn_gnr_basket']:
    #             if not self._genres.has(genre_id):
    #                 self._genres.get_or_create(id=genre_id, name=None)

    #             genre = self._genres.get(genre_id)
    #             self._edges.get_or_create(
    #                 song, genre, SongNode.Relation.GENRE)
    #             self._edges.get_or_create(
    #                 genre, song, GenreNode.Relation.SONG)

    #         for detailed_genre_id in song_meta['song_gn_dtl_gnr_basket']:
    #             if not self._genres.has(detailed_genre_id):
    #                 self._genres.get_or_create(id=detailed_genre_id, name=None)

    #             detailed_genre = self._genres.get(detailed_genre_id)
    #             self._edges.get_or_create(
    #                 song, detailed_genre, SongNode.Relation.DETAILED_GENRE)
    #             self._edges.get_or_create(
    #                 detailed_genre, song, GenreNode.Relation.SONG)

    # def _parse_playlists(self, playlists):
    #     for playlist in tqdm(playlists, "Parsing playlists"):
    #         playlist = self._playlists.get_or_create(
    #             id=playlist['id'],
    #             name=playlist['plylst_title'],
    #             like_count=playlist['like_cnt'],
    #             update_date=playlist['updt_date'],
    #         )

    #         for tag_name in playlist['tags']:
    #             tag = self._tags.get_or_create(
    #                 id=tag_name,
    #                 name=tag_name,
    #             )
    #             self._edges.get_or_create(
    #                 playlist, tag, PlaylistNode.Relation.TAG)
    #             self._edges.get_or_create(
    #                 tag, playlist, TagNode.Relation.PLAYLIST)

    #         for song_id in playlist['songs']:
    #             song = self._songs.get(song_id)
    #             self._edges.get_or_create(
    #                 playlist, song, PlaylistNode.Relation.SONG)
    #             self._edges.get_or_create(
    #                 song, playlist, SongNode.Relation.PLAYLIST)

    # @staticmethod
    # def _validate_song(song, id, name, issue_date):
    #     return (
    #         (song.id == id) and
    #         (song.name == name) and
    #         (song.issue_date == issue_date)
    #     )

    # @staticmethod
    # def _validate_album(album, id, name):
    #     # id가 동일해도 name이 다른 경우가 많음.
    #     return album.id == id

    # @staticmethod
    # def _validate_artist(artist, id, name):
    #     # id가 동일해도 name이 다른 경우가 많음.
    #     return artist.id == id

    # @staticmethod
    # def _validate_genre(genre, id, name):
    #     return (genre.id == id) and (genre.name == name)

    # @staticmethod
    # def _validate_tag(tag, id, name):
    #     return (tag.id == id) and (tag.name == name)

    # @staticmethod
    # def _validate_playlist(playlist, id, name, like_count, update_date):
    #     return (
    #         (playlist.id == id) and
    #         (playlist.name == name) and
    #         (playlist.like_count == like_count) and
    #         (playlist.update_date == update_date)
    #     )
