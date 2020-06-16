from tqdm import tqdm
from ..core import Graph
from ..nodes import (
    AlbumNode, ArtistNode, GenreNode, PlaylistNode, SongNode, TagNode)
from .node_manager import NodeManager
from .edge_manager import EdgeManager


class GraphBuilder:
    def __init__(self, song_meta, genre_gn_all, playlists):
        self.song_meta = song_meta
        self.genre_gn_all = genre_gn_all
        self.playlists = playlists

        self._graph = None
        self._albums = None
        self._artists = None
        self._genres = None
        self._playlists = None
        self._songs = None
        self._tags = None
        self._edges = None

    def build(self):
        self._initialize()
        self._parse_genres(self.genre_gn_all)
        self._parse_songs(self.song_meta)
        self._parse_playlists(self.playlists)

        return self._graph

    def _initialize(self):
        self._graph = Graph()
        self._albums = NodeManager(
            self._graph, AlbumNode, GraphBuilder._validate_album)
        self._artists = NodeManager(
            self._graph, ArtistNode, GraphBuilder._validate_artist)
        self._genres = NodeManager(
            self._graph, GenreNode, GraphBuilder._validate_genre)
        self._playlists = NodeManager(
            self._graph, PlaylistNode, GraphBuilder._validate_playlist)
        self._songs = NodeManager(
            self._graph, SongNode, GraphBuilder._validate_song)
        self._tags = NodeManager(
            self._graph, TagNode, GraphBuilder._validate_tag)
        self._edges = EdgeManager(self._graph)

    def _parse_genres(self, genre_gn_all):
        for key, value in tqdm(genre_gn_all.items(), "Parsing genres"):
            self._genres.get_or_create(id=key, name=value)

    def _parse_songs(self, song_metas):
        for song_meta in tqdm(song_metas, "Parsing songs"):
            song = self._songs.get_or_create(
                id=song_meta['id'],
                name=song_meta['song_name'],
                issue_date=song_meta['issue_date'],
            )

            artists = zip(song_meta['artist_id_basket'],
                          song_meta['artist_name_basket'])
            for artist_id, artist_name in artists:
                artist = self._artists.get_or_create(
                    id=artist_id,
                    name=artist_name,
                )
                self._edges.get_or_create(
                    song, artist, SongNode.Relation.ARTIST)
                self._edges.get_or_create(
                    artist, song, ArtistNode.Relation.SONG)

            album = self._albums.get_or_create(
                id=song_meta['album_id'],
                name=song_meta['album_name'],
            )
            self._edges.get_or_create(song, album, SongNode.Relation.ALBUM)
            self._edges.get_or_create(album, song, AlbumNode.Relation.SONG)

            for genre_id in song_meta['song_gn_gnr_basket']:
                if not self._genres.has(genre_id):
                    self._genres.get_or_create(id=genre_id, name=None)

                genre = self._genres.get(genre_id)
                self._edges.get_or_create(
                    song, genre, SongNode.Relation.GENRE)
                self._edges.get_or_create(
                    genre, song, GenreNode.Relation.SONG)

            for detailed_genre_id in song_meta['song_gn_dtl_gnr_basket']:
                if not self._genres.has(detailed_genre_id):
                    self._genres.get_or_create(id=detailed_genre_id, name=None)

                detailed_genre = self._genres.get(detailed_genre_id)
                self._edges.get_or_create(
                    song, detailed_genre, SongNode.Relation.DETAILED_GENRE)
                self._edges.get_or_create(
                    detailed_genre, song, GenreNode.Relation.SONG)

    def _parse_playlists(self, playlists):
        for playlist_meta in tqdm(playlists, "Parsing playlists"):
            playlist = self._playlists.get_or_create(
                id=playlist_meta['id'],
                name=playlist_meta['plylst_title'],
                like_count=playlist_meta['like_cnt'],
                update_date=playlist_meta['updt_date'],
            )

            for tag_name in playlist_meta['tags']:
                tag = self._tags.get_or_create(
                    id=tag_name,
                    name=tag_name,
                )
                self._edges.get_or_create(
                    playlist, tag, PlaylistNode.Relation.TAG)
                self._edges.get_or_create(
                    tag, playlist, TagNode.Relation.PLAYLIST)

            for song_id in playlist_meta['songs']:
                song = self._songs.get(song_id)
                self._edges.get_or_create(
                    playlist, song, PlaylistNode.Relation.SONG)
                self._edges.get_or_create(
                    song, playlist, SongNode.Relation.PLAYLIST)

    @staticmethod
    def _validate_song(song, id, name, issue_date):
        return (
            (song.id == id) and
            (song.name == name) and
            (song.issue_date == issue_date)
        )

    @staticmethod
    def _validate_album(album, id, name):
        # id가 동일해도 name이 다른 경우가 많음.
        return album.id == id

    @staticmethod
    def _validate_artist(artist, id, name):
        # id가 동일해도 name이 다른 경우가 많음.
        return artist.id == id

    @staticmethod
    def _validate_genre(genre, id, name):
        return (genre.id == id) and (genre.name == name)

    @staticmethod
    def _validate_tag(tag, id, name):
        return (tag.id == id) and (tag.name == name)

    @staticmethod
    def _validate_playlist(playlist, id, name, like_count, update_date):
        return (
            (playlist.id == id) and
            (playlist.name == name) and
            (playlist.like_count == like_count) and
            (playlist.update_date == update_date)
        )
