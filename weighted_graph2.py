# -*- coding: utf-8 -*-
from collections import Counter
import heapq
import fire
from tqdm import tqdm
import pickle
from arena_util import write_json, load_json_to_df, load_json
import pandas as pd
import os
import random
import numpy as np


class GraphCF:
    def _song_meta_to_graph(self, song_meta_df):

        if os.path.isfile('./res/meta_graph.graph'):
            with open('./res/meta_graph.graph', 'rb') as f:
                data = pickle.load(f)
                return data

        # song_meta_graph 구성 - >  [ song_id 707989 개] [소장르 225 개] [대장르 30 개] [앨범 287235 개] [아티스트 115457 개]

        song_meta_graph = {}
        song_meta_graph_len = 0

        # song 노드 추가
        print("song hashing...")
        song_len = len(song_meta_df)
        for i in range(song_len):
            song_meta_graph[song_meta_graph_len + i] = []

        song_meta_graph_len = song_meta_graph_len + song_len
        # 소장르 대장르 매핑 그래프

        # 예제 코드 그대로 사용
        genre_gn_all = pd.read_json('res/genre_gn_all.json', typ='series', encoding='UTF-8')
        genre_gn_all = pd.DataFrame(genre_gn_all, columns=['gnr_name']).reset_index().rename(
            columns={'index': 'gnr_code'})
        gnr_code = genre_gn_all[genre_gn_all['gnr_code'].str[-2:] == '00']
        dtl_gnr_code = genre_gn_all[genre_gn_all['gnr_code'].str[-2:] != '00']
        dtl_gnr_code.rename(columns={'gnr_code': 'dtl_gnr_code', 'gnr_name': 'dtl_gnr_name'}, inplace=True)
        gnr_code = gnr_code.assign(join_code=gnr_code['gnr_code'].str[0:4])
        dtl_gnr_code = dtl_gnr_code.assign(join_code=dtl_gnr_code['dtl_gnr_code'].str[0:4])
        gnr_code_tree = pd.merge(gnr_code, dtl_gnr_code, how='left', on='join_code')
        gnr_df = gnr_code_tree[['gnr_code', 'gnr_name', 'dtl_gnr_code', 'dtl_gnr_name']]

        # 크리스마스 장르만 세부장르가 없으므로 세부장르 만들었습니다.

        gnr_df.loc[224, ['dtl_gnr_code']] = "GN3001"
        gnr_df.loc[224, ['dtl_gnr_name']] = "세부장르전체"

        #  소장르 노드 추가 및 hash
        print("dtl_gnr hashing...")
        dtl_gnr_hash = {}
        dtl_gnr_len = len(gnr_df)
        for idx in range(dtl_gnr_len):
            song_meta_graph[song_meta_graph_len + idx] = []
            dtl_gnr_hash[gnr_df.loc[idx, ['dtl_gnr_code']][0]] = song_meta_graph_len + idx

        song_meta_graph_len = song_meta_graph_len + dtl_gnr_len

        #  대장르 노드 추가 및 hash
        gnr_hash = {}
        gnr_len = len(gnr_code)
        print("gnr hashing...")
        for idx in range(gnr_len):
            song_meta_graph[song_meta_graph_len + idx] = []
            gnr_hash[gnr_code.iloc[idx, 0]] = song_meta_graph_len + idx

        song_meta_graph_len = song_meta_graph_len + gnr_len

        # 소장르 - 대장르 엣지 추가
        print("gnr edge...")
        for idx in range(dtl_gnr_len):
            dtl_gnr = gnr_df.loc[idx, ['dtl_gnr_code']][0]
            gnr = gnr_df.loc[idx, ['gnr_code']][0]

            # dtl_gnr -> gnr
            song_meta_graph[dtl_gnr_hash[dtl_gnr]].append(gnr_hash[gnr])

            # dtl_gnr <- gnr
            song_meta_graph[gnr_hash[gnr]].append(dtl_gnr_hash[dtl_gnr])

        # 앨범 노드 추가 및 hash
        print("album hashing...")
        album = song_meta_df['album_id'].value_counts()
        album_hash = album.to_dict()
        album_len = len(album_hash)

        for idx, (key, val) in tqdm(enumerate(album_hash.items())):
            song_meta_graph[song_meta_graph_len + idx] = []
            album_hash[key] = song_meta_graph_len + idx

        song_meta_graph_len = song_meta_graph_len + album_len

        # 아티스트 노드 추가 및 hash
        artist_counter = Counter()
        print("artist hashing...")
        for idx in tqdm(range(len(song_meta_df))):
            artist_id_list = song_meta_df.loc[idx, ['artist_id_basket']]
            artist_counter.update(artist_id_list[0])

        artist_hash = dict(artist_counter)
        artist_len = len(artist_hash)
        for idx, (key, val) in enumerate(artist_hash.items()):
            song_meta_graph[song_meta_graph_len + idx] = []
            artist_hash[key] = song_meta_graph_len + idx

        song_meta_graph_len = song_meta_graph_len + artist_len

        # song 전체 읽으면서 song - dtl_gnr , song - album , album - artist 엣지 연결
        print("edge...")
        for idx in tqdm(range(len(song_meta_df))):

            # song - dtl_gnr
            dtl_gnr_list = song_meta_df.loc[idx, ['song_gn_dtl_gnr_basket']][0]

            # 크리스마스 장르 있으면 크리스마스 소장르 추가
            gnr_list = song_meta_df.loc[idx, ['song_gn_gnr_basket']][0]
            if "GN3001" in gnr_list:
                dtl_gnr_list.append("GN3001")

            for song_dtl_gnr in dtl_gnr_list:
                song_meta_graph[idx].append(dtl_gnr_hash[song_dtl_gnr])
                song_meta_graph[dtl_gnr_hash[song_dtl_gnr]].append(idx)

            # song - album

            song_album = song_meta_df.loc[idx, ['album_id']][0]
            song_meta_graph[idx].append(album_hash[song_album])
            song_meta_graph[album_hash[song_album]].append(idx)

            # album - artist

            artist_list = song_meta_df.loc[idx, ['artist_id_basket']][0]

            for song_artist in artist_list:
                if not album_hash[song_album] in song_meta_graph[artist_hash[song_artist]]:
                    song_meta_graph[album_hash[song_album]].append(artist_hash[song_artist])
                    song_meta_graph[artist_hash[song_artist]].append(album_hash[song_album])

        with open('./res/meta_graph.graph', 'wb') as f:
            pickle.dump(song_meta_graph, f)

        return song_meta_graph

    def _generate_answers(self, meta_song_graph, train, questions):

        # train   play_list, tag 노드 만들기 , play_list - song, play_list - tag 엣지 만들기

        print("train tags... ")
        tag_counter = Counter()
        meta_song_len = len(meta_song_graph)

        paly_list_hash = {}
        for idx in tqdm(range(len(train))):
            tag = train.loc[idx, ['tags']][0]
            meta_song_graph[meta_song_len + idx] = []
            paly_list_hash[idx] = meta_song_len + idx
            tag_counter.update(tag)

        meta_song_len = len(meta_song_graph)
        tag_hash = dict(tag_counter)
        reverse_tag_hash = {}

        for idx, (key, val) in enumerate(tag_hash.items()):
            meta_song_graph[meta_song_len + idx] = []
            tag_hash[key] = meta_song_len + idx
            reverse_tag_hash[meta_song_len + idx] = key

        tag_start_idx = meta_song_len
        tag_end_idx = len(meta_song_graph) - 1

        print("train edge...")
        for idx in tqdm(range(len(train))):
            songs = train.loc[idx, ['songs']][0]

            for song in songs:
                meta_song_graph[song].append(paly_list_hash[idx])
                meta_song_graph[paly_list_hash[idx]].append(song)
            tags = train.loc[idx, ['tags']][0]

            for tag in tags:
                meta_song_graph[paly_list_hash[idx]].append(tag_hash[tag])
                meta_song_graph[tag_hash[tag]].append(paly_list_hash[idx])

        answers = []
        print("make answer...")

        score_map = {}
        score_map['노래'] = {}
        score_map['소장르'] = {}
        score_map['대장르'] = {}
        score_map['앨범'] = {}
        score_map['가수'] = {}
        score_map['플레이리스트'] = {}
        score_map['태그'] = {}

        score_map['노래']['플레이리스트'] = 6
        score_map['플레이리스트']['노래'] = 0

        score_map['태그']['플레이리스트'] = 3
        score_map['플레이리스트']['태그'] = 0

        score_map['노래']['소장르'] = 2.5
        score_map['소장르']['노래'] = 0

        score_map['소장르']['대장르'] = 1.5
        score_map['대장르']['소장르'] = 0

        score_map['노래']['앨범'] = 4
        score_map['앨범']['노래'""] = 0

        score_map['앨범']['가수'] = 3
        score_map['가수']['앨범'] = 0

        def check_node(x):
            node = ''
            if x < 707989:
                # print("song")
                node = '노래'
            elif x < 707989 + 225:
                # print("소장르")
                node = "소장르"
            elif x < 707989 + 225 + 30:
                # print("대장르")
                node = '대장르'
            elif x < 707989 + 225 + 30 + 287235:
                node = '앨범'
            elif x < 707989 + 225 + 30 + 287235 + 115457:
                node = '가수'
            elif x < tag_start_idx:
                node = '플레이리스트'
            else:
                node = '태그'
            return node

        for q in tqdm(questions):
            rec_song_list = []
            rec_tag_list = []

            score_list = [0 for _ in range(len(meta_song_graph))]
            vist_list = [False for _ in range(len(meta_song_graph))]

            queue_list = []

            my_songs = q['songs']
            my_tags = q['tags']

            for my_song in my_songs:
                vist_list[my_song] = True
                queue_list.append(my_song)

            for my_tag in my_tags:
                if my_tag in tag_hash.keys():
                    vist_list[tag_hash[my_tag]] = True
                    queue_list.append(tag_hash[my_tag])


            # tag랑 songs가 빈 question이 있어서 랜덤으로 뿌려준다. 
            if len(queue_list) ==0:
                while len(rec_song_list) != 100:
                    rand_id = random.randint(1, 707989)
                    while rand_id in rec_song_list:
                        rand_id = random.randint(1, 700000)
                    rec_song_list.append(rand_id)
                while len(rec_tag_list) != 10:
                    rand_id = random.randint(tag_start_idx, tag_end_idx)
                    while rand_id in rec_tag_list:
                        rand_id = random.randint(tag_start_idx, tag_end_idx)
                    rec_tag_list.append(rand_id)

                for idx,val in enumerate(rec_tag_list):
                    rec_tag_list[idx]=reverse_tag_hash[val]

                answers.append({
                    "id": q["id"],
                    "songs": rec_song_list,
                    "tags": rec_tag_list
                })
                continue

            
            # score 연산 시작
            condition_node = queue_list[-1]
            while  len(rec_song_list)!=100 or  len(rec_tag_list)!=10 :

                cur = queue_list.pop(0)

                for nearest in meta_song_graph[cur]:
                    node_cur = check_node(cur)
                    node_nearest = check_node(nearest)
                    score_list[nearest] = score_list[nearest] + score_list[cur] + score_map[node_cur][node_nearest]
                    if not vist_list[nearest]:
                        vist_list[nearest] = True
                        queue_list.append(nearest)

                # depth 탐색 종료
                if condition_node == cur:

                    song_heap = []
                    tag_heap = []

                    for idx , val in enumerate(score_list):
                        # song node 일때
                        if len(rec_song_list)!=100:
                            if idx < 707989 and score_list[idx]>1:
                                if not idx in rec_song_list :
                                    if not idx in my_songs:
                                        heapq.heappush(song_heap, (-val, idx))

                            # tag node 일떄

                            if len(rec_song_list)==100 :
                                song_list_100 = True

                        if len(rec_tag_list)!=10:

                            if tag_start_idx <= idx and idx <= tag_end_idx and score_list[idx]>1:
                                if not reverse_tag_hash[idx] in rec_tag_list:
                                    if not reverse_tag_hash[idx] in my_tags:
                                        heapq.heappush(tag_heap, (-val, idx))
                    while len(rec_song_list) != 100 and len(song_heap) != 0:
                        rec_song_list.append(heapq.heappop(song_heap)[1])
                    while len(rec_tag_list)!=10 and len(tag_heap) != 0:
                        rec_tag_list.append(reverse_tag_hash[heapq.heappop(tag_heap)[1]])
                    condition_node = queue_list[-1]


            if len(rec_song_list) != 100:
                print(f'song sz : {len(rec_song_list)}')
            if len(rec_tag_list) != 10:
                print(f'tag sz : {len(rec_tag_list)}')

            answers.append({
                "id": q["id"],
                "songs": rec_song_list,
                "tags": rec_tag_list
            })

        return answers

    def run(self, song_meta_fname, train_fname, question_fname):

        print("Loading song meta...")
        song_meta_df = load_json_to_df(song_meta_fname)

        meta_song_graph = self._song_meta_to_graph(song_meta_df)

        print("Loading train file...")
        train_data = load_json_to_df(train_fname)

        print("Loading question file...")
        questions = load_json(question_fname)

        print("Writing answers...")

        answers = self._generate_answers(meta_song_graph, train_data, questions)
        write_json(answers, "results/results.json")


if __name__ == "__main__":
    fire.Fire(GraphCF)
