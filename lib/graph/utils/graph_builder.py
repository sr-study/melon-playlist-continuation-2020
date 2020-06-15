from ..core import Graph
from ..nodes import AlbumNode, ArtistNode, GenreNode, PlaylistNode, SongNode, TagNode
from .node_manager import NodeManager


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

    def build(self):
        self._initialize()
        self._parse_genres(self.genre_gn_all)
        self._parse_songs(self.song_meta)
        self._parse_playlists(self.playlists)

        return self._graph

    def _initialize(self):
        self._graph = Graph()
        self._albums = NodeManager(self._graph, AlbumNode, GraphBuilder._validate_album)
        self._artists = NodeManager(self._graph, ArtistNode, GraphBuilder._validate_artist)
        self._genres = NodeManager(self._graph, GenreNode, GraphBuilder._validate_genre)
        self._playlists = NodeManager(self._graph, PlaylistNode, GraphBuilder._validate_playlist)
        self._songs = NodeManager(self._graph, SongNode, GraphBuilder._validate_song)
        self._tags = NodeManager(self._graph, TagNode, GraphBuilder._validate_tag)

    def _parse_genres(self, genre_gn_all):
        for key, value in genre_gn_all.items():
            self._genres.get_or_create(id=key, name=value)

    def _parse_songs(self, song_metas):
        for song_meta in song_metas:
            song = self._songs.get_or_create(
                id=song_meta['id'],
                name=song_meta['song_name'],
                issue_date=song_meta['issue_date'],
            )

            for artist_id, artist_name in zip(song_meta['artist_id_basket'], song_meta['artist_name_basket']):
                artist = self._artists.get_or_create(
                    id=artist_id,
                    name=artist_name,
                )
                self._graph.add_edge(song, artist, SongNode.Relation.ARTIST)
                self._graph.add_edge(artist, song, ArtistNode.Relation.SONG)

            album = self._albums.get_or_create(
                id=song_meta['album_id'],
                name=song_meta['album_name'],
            )
            self._graph.add_edge(song, album, SongNode.Relation.ALBUM)
            self._graph.add_edge(album, song, AlbumNode.Relation.SONG)

    def _parse_playlists(self, playlists):
        for playlist_meta in playlists:
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
                self._graph.add_edge(playlist, tag, PlaylistNode.Relation.TAG)
                self._graph.add_edge(tag, playlist, TagNode.Relation.PLAYLIST)

            for song_id in playlist_meta['songs']:
                song = self._songs.get(song_id)
                self._graph.add_edge(playlist, song, PlaylistNode.Relation.SONG)
                self._graph.add_edge(song, playlist, SongNode.Relation.PLAYLIST)

    @staticmethod
    def _validate_song(song, id, name, issue_date):
        if song.id != id: return False
        if song.name != name: return False
        if song.issue_date != issue_date: return False
        return True

    @staticmethod
    def _validate_album(album, id, name):
        if album.id != id: return False
        # id가 동일해도 name이 다른 경우가 많음.
#         if album.name != name: return False
        return True

    @staticmethod
    def _validate_artist(artist, id, name):
        if artist.id != id: return False
        # id가 동일해도 name이 다른 경우가 많음.
#         if artist.name != name: return False
        return True

    @staticmethod
    def _validate_genre(genre, id, name):
        if genre.id != id: return False
        if genre.name != name: return False
        return True

    @staticmethod
    def _validate_tag(tag, id, name):
        if tag.id != id: return False
        if tag.name != name: return False
        return True

    @staticmethod
    def _validate_playlist(playlist, id, name, like_count, update_date):
        if playlist.id != id: return False
        if playlist.name != name: return False
        if playlist.like_count != like_count: return False
        if playlist.update_date != update_date: return False
        return True
