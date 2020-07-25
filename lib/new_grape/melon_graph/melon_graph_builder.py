from tqdm import tqdm
from .melon_graph import MelonGraph
from .utils import get_words
from ..graph import Edge
from ..graph import Graph
from ..graph import Node


class MelonGraphBuilder:
    def build(self, songs, genres, playlists, verbose=True):
        raw_nodes, raw_edges = self._parse_all(songs, genres, playlists, verbose)
        return self._create_graph(raw_nodes, raw_edges, verbose)

    def _parse_all(self, songs, genres, playlists, verbose=True):
        pbar = None
        if verbose:
            total = len(genres) + len(songs) + len(playlists)
            pbar = tqdm(desc="Parsing data", total=total)

        raw_nodes = []
        raw_edges = []

        parsed_raw_nodes, parsed_raw_edges = self._parse_genres(genres, pbar)
        raw_nodes += parsed_raw_nodes
        raw_edges += parsed_raw_edges

        parsed_raw_nodes, parsed_raw_edges = self._parse_songs(songs, pbar)
        raw_nodes += parsed_raw_nodes
        raw_edges += parsed_raw_edges

        parsed_raw_nodes, parsed_raw_edges = self._parse_playlists(playlists, pbar)
        raw_nodes += parsed_raw_nodes
        raw_edges += parsed_raw_edges

        if pbar is not None:
            pbar.close()

        return raw_nodes, raw_edges

    def _parse_genres(self, genres, pbar=None):
        raw_nodes = []
        raw_edges = []

        for key, value in genres.items():
            raw_nodes.append((MelonGraph.NodeType.GENRE, key, {
                'name': value
            }))

            if pbar is not None:
                pbar.update()

        return raw_nodes, raw_edges

    def _parse_songs(self, songs, pbar=None):
        raw_nodes = []
        raw_edges = []

        for song in songs:
            song_key = (MelonGraph.NodeType.SONG, song['id'])
            raw_nodes.append((MelonGraph.NodeType.SONG, song['id'], {
                'name': song['song_name'],
                'issue_date': song['issue_date'],
            }))

            artist_keys = []
            artists = zip(song['artist_id_basket'], song['artist_name_basket'])
            for artist_id, artist_name in artists:
                artist_key = (MelonGraph.NodeType.ARTIST, artist_id)
                artist_keys.append(artist_key)
                raw_nodes.append((MelonGraph.NodeType.ARTIST, artist_id, {
                    'name': artist_name,
                }))
                raw_edges.append((
                    song_key,
                    artist_key,
                    MelonGraph.Relation.SONG_TO_ARTIST,
                ))
                raw_edges.append((
                    artist_key,
                    song_key,
                    MelonGraph.Relation.ARTIST_TO_SONG,
                ))

                for word in get_words(artist_name):
                    word_key = (MelonGraph.NodeType.WORD, word)
                    raw_nodes.append((MelonGraph.NodeType.WORD, word, {}))
                    raw_edges.append((
                        artist_key,
                        word_key,
                        MelonGraph.Relation.ARTIST_TO_WORD,
                    ))
                    raw_edges.append((
                        word_key,
                        artist_key,
                        MelonGraph.Relation.WORD_TO_ARTIST,
                    ))

            album_key = (MelonGraph.NodeType.ALBUM, song['album_id'])
            raw_nodes.append((MelonGraph.NodeType.ALBUM, song['album_id'], {
                'name': song['album_name'],
            }))
            raw_edges.append((
                song_key,
                album_key,
                MelonGraph.Relation.SONG_TO_ARTIST,
            ))
            raw_edges.append((
                album_key,
                song_key,
                MelonGraph.Relation.ALBUM_TO_SONG,
            ))

            if song['album_name'] is not None:
                for word in get_words(song['album_name']):
                    word_key = (MelonGraph.NodeType.WORD, word)
                    raw_nodes.append((MelonGraph.NodeType.WORD, word, {}))
                    raw_edges.append((
                        album_key,
                        word_key,
                        MelonGraph.Relation.ALBUM_TO_WORD,
                    ))
                    raw_edges.append((
                        word_key,
                        album_key,
                        MelonGraph.Relation.WORD_TO_ALBUM,
                    ))

            for genre_id in song['song_gn_gnr_basket']:
                genre_key = (MelonGraph.NodeType.GENRE, genre_id)
                raw_edges.append((
                    song_key,
                    genre_key,
                    MelonGraph.Relation.SONG_TO_GENRE,
                ))
                raw_edges.append((
                    genre_key,
                    song_key,
                    MelonGraph.Relation.GENRE_TO_SONG,
                ))

                for artist_key in artist_keys:
                    artist_genre_key = (
                        MelonGraph.NodeType.ARTIST_GENRE, (artist_key[1], genre_key[1]))
                    raw_nodes.append((artist_genre_key[0], artist_genre_key[1], {}))
                    raw_edges.append((
                        song_key,
                        artist_genre_key,
                        MelonGraph.Relation.ARTIST_GENRE_TO_SONG,
                    ))
                    raw_edges.append((
                        artist_genre_key,
                        song_key,
                        MelonGraph.Relation.SONG_TO_ARTIST_GENRE,
                    ))

            for genre_id in song['song_gn_dtl_gnr_basket']:
                genre_key = (MelonGraph.NodeType.GENRE, genre_id)
                raw_edges.append((
                    song_key,
                    genre_key,
                    MelonGraph.Relation.SONG_TO_DETAILED_GENRE,
                ))
                raw_edges.append((
                    genre_key,
                    song_key,
                    MelonGraph.Relation.GENRE_TO_SONG,
                ))

                for artist_key in artist_keys:
                    artist_genre_key = (
                        MelonGraph.NodeType.ARTIST_GENRE, (artist_key[1], genre_key[1]))
                    raw_nodes.append((artist_genre_key[0], artist_genre_key[1], {}))
                    raw_edges.append((
                        song_key,
                        artist_genre_key,
                        MelonGraph.Relation.ARTIST_GENRE_TO_SONG,
                    ))
                    raw_edges.append((
                        artist_genre_key,
                        song_key,
                        MelonGraph.Relation.SONG_TO_ARTIST_DETAILED_GENRE,
                    ))

            issue_date = song['issue_date']
            year = int(issue_date[0:4])
            month = int(issue_date[4:6])
            if year > 0:
                year_key = (MelonGraph.NodeType.YEAR, year)
                raw_edges.append((
                    song_key,
                    year_key,
                    MelonGraph.Relation.SONG_TO_YEAR,
                ))
                raw_edges.append((
                    year_key,
                    song_key,
                    MelonGraph.Relation.YEAR_TO_SONG,
                ))
            if month > 0:
                month_key = (MelonGraph.NodeType.MONTH, month)
                raw_edges.append((
                    song_key,
                    month_key,
                    MelonGraph.Relation.SONG_TO_MONTH,
                ))
                raw_edges.append((
                    month_key,
                    song_key,
                    MelonGraph.Relation.MONTH_TO_SONG,
                ))

            if pbar is not None:
                pbar.update()

        return raw_nodes, raw_edges

    def _parse_playlists(self, playlists, pbar=None):
        raw_nodes = []
        raw_edges = []

        for playlist in playlists:
            playlist_key = (MelonGraph.NodeType.PLAYLIST, playlist['id'])
            raw_nodes.append((MelonGraph.NodeType.PLAYLIST, playlist['id'], {
                'name': playlist['plylst_title'],
                'like_count': playlist['like_cnt'],
                'update_date': playlist['updt_date'],
            }))

            for tag in playlist['tags']:
                tag_key = (MelonGraph.NodeType.TAG, tag)
                raw_nodes.append((MelonGraph.NodeType.TAG, tag, {}))
                raw_edges.append((
                    playlist_key,
                    tag_key,
                    MelonGraph.Relation.PLAYLIST_TO_TAG,
                ))
                raw_edges.append((
                    tag_key,
                    playlist_key,
                    MelonGraph.Relation.TAG_TO_PLAYLIST,
                ))

                for word in get_words(tag):
                    word_key = (MelonGraph.NodeType.WORD, word)
                    raw_nodes.append((MelonGraph.NodeType.WORD, word, {}))
                    raw_edges.append((
                        tag_key,
                        word_key,
                        MelonGraph.Relation.TAG_TO_WORD,
                    ))
                    raw_edges.append((
                        word_key,
                        tag_key,
                        MelonGraph.Relation.WORD_TO_TAG,
                    ))

            for song_id in playlist['songs']:
                song_key = (MelonGraph.NodeType.SONG, song_id)
                raw_edges.append((
                    playlist_key,
                    song_key,
                    MelonGraph.Relation.PLAYLIST_TO_SONG,
                ))
                raw_edges.append((
                    song_key,
                    playlist_key,
                    MelonGraph.Relation.SONG_TO_PLAYLIST,
                ))

            for word in get_words(playlist['plylst_title']):
                word_key = (MelonGraph.NodeType.WORD, word)
                raw_nodes.append((MelonGraph.NodeType.WORD, word, {}))
                raw_edges.append((
                    playlist_key,
                    word_key,
                    MelonGraph.Relation.PLAYLIST_TO_WORD,
                ))
                raw_edges.append((
                    word_key,
                    playlist_key,
                    MelonGraph.Relation.WORD_TO_PLAYLIST,
                ))

            if pbar is not None:
                pbar.update()

        return raw_nodes, raw_edges

    def _create_graph(self, raw_nodes, raw_edges, verbose=True):
        pbar = None
        if verbose:
            total = len(raw_nodes) + len(raw_edges)
            pbar = tqdm(desc="Creating graph", total=total)

        graph = Graph()
        self._add_nodes(graph, raw_nodes, pbar)
        self._add_edges(graph, raw_edges, pbar)

        if pbar is not None:
            pbar.close()

        return graph

    def _add_nodes(self, graph, raw_nodes, pbar=None):
        node_keys = set()
        for raw_node in raw_nodes:
            node_type, node_id, data = raw_node

            node_key = (node_type, node_id)
            if node_key in node_keys:
                if pbar is not None:
                    pbar.update()
                continue

            node_keys.add(node_key)

            node = Node(node_type, node_id, data)
            graph.add_node(node)

            if pbar is not None:
                pbar.update()

    def _add_edges(self, graph, raw_edges, pbar=None):
        node_key_index = {}
        for index, node in enumerate(graph.nodes):
            node_key = (node.type, node.id)
            node_key_index[node_key] = index

        def __has_node_index(node_type, node_id):
            node_key = (node_type, node_id)
            return node_key in node_key_index

        def __get_node_index(node_type, node_id):
            node_key = (node_type, node_id)
            return node_key_index[node_key]

        def __add_node(node):
            node_key = (node.type, node.id)
            node_index = len(graph.nodes)
            graph.add_node(node)
            node_key_index[node_key] = node_index
            return node_index

        edge_keys = set()
        for raw_edge in raw_edges:
            src, dst, relation = raw_edge

            edge_key = raw_edge
            if edge_key in edge_keys:
                if pbar is not None:
                    pbar.update()
                continue

            edge_keys.add(edge_key)

            if __has_node_index(src[0], src[1]):
                src_index = __get_node_index(src[0], src[1])
            else:
                src_index = __add_node(Node(src[0], src[1], {}))

            if __has_node_index(dst[0], dst[1]):
                dst_index = __get_node_index(dst[0], dst[1])
            else:
                dst_index = __add_node(Node(dst[0], dst[1], {}))

            edge = Edge(src_index, dst_index, relation)
            graph.add_edge(edge)

            if pbar is not None:
                pbar.update()
