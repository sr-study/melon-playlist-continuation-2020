# -*- coding: utf-8 -*-
from collections import Counter

import fire
from tqdm import tqdm
import random
from arena_util import load_json
from arena_util import write_json
from arena_util import remove_seen
from arena_util import most_popular


class GenreMostPopular:
    def _song_mp_per_genre(self, song_meta, global_mp):
        res = {}

        for sid, song in song_meta.items():
            for genre in song['song_gn_gnr_basket']:
                res.setdefault(genre, []).append(sid)

        for genre, sids in res.items():
            res[genre] = Counter({k: global_mp.get(int(k), 0) for k in sids})
            res[genre] = [k for k, v in res[genre].most_common(200)]

        return res


    def _weighted_graph(self,train):
        edge_dict = {}
        print ("weighted_graph",flush=True)
        for t in  tqdm(train):
            songs=t['songs']
            for left in range(len(songs)):
                for right in range(left,len(songs)):

                    # left -> right
                    if not songs[left] in edge_dict:
                        edge_dict[songs[left]]={}

                    if not songs[right] in edge_dict[songs[left]]:
                        edge_dict[songs[left]][songs[right]]=0

                    edge_dict[songs[left]][songs[right]]=edge_dict[songs[left]][songs[right]]+1

                    # left <- right

                    if not songs[right] in edge_dict:
                        edge_dict[songs[right]]={}

                    if not songs[left] in edge_dict[songs[right]]:
                        edge_dict[songs[right]][songs[left]]=0

                    edge_dict[songs[right]][songs[left]]=edge_dict[songs[right]][songs[left]]+1

        return edge_dict






    def _train_playlist(self, train):
        tag_lists = []
        song_lists = []

        for t in train:
            tag_lists.append(set(t['tags']))
            song_lists.append(set(t['songs']))

        return song_lists, tag_lists


    def _get_weighted_graph_song_recommends(self,my_songs,song_weighted_graph):
        depth_one_counter = Counter()

        for song in my_songs:
            if song in song_weighted_graph:
                depth_one_counter.update(song_weighted_graph[song])
        depth_one_sorted_list = depth_one_counter.most_common()

        answer = []
        # 기존에 있던 애들을 제외하고 나머지 애들을 순서대로 뽑아서 정답으로 한다
        for candidate in depth_one_sorted_list:
            if len(answer) is 100:
                break
            if not candidate[0] in my_songs:
                answer.append(candidate[0])
        while len(answer) != 100:
            rand_id = random.randint(1,700000)
            while rand_id in answer:
                rand_id = random.randint(1, 700000)
            answer.append(rand_id)
        return answer








    def _get_song_recommends(self, song_sets, my_songs, sorted_list, my_artists, my_genres, song_meta):
        rec_song_list = list()
        weight = []
        song_weights = Counter()

        for i in range(20):
            weight.append(sorted_list[i][0])

        for i in range(20):
            if sorted_list[i][0] == 0:
                break
            cur_playlist = song_sets[sorted_list[i][1]]
            for song in cur_playlist:
                if song not in my_songs:
                    song_weights[song] += weight[i]
                    cur_artists = song_meta[song]['artist_id_basket']
                    chk = False
                    for artist in cur_artists:
                        if artist in my_artists:
                            chk = True
                            break
                    if chk:
                        song_weights[song] += (weight[i] // 4)

                    cur_genres = song_meta[song]['song_gn_dtl_gnr_basket']
                    tot_num = len(cur_genres)
                    matched_num = 0
                    for genre in cur_genres:
                        if genre in my_genres:
                            matched_num += 2
                    if matched_num:
                        #w = int((matched_num / tot_num)*(weight[i] // 2))
                        song_weights[song] += int((matched_num / tot_num)*(weight[i] / 5))

        song_weights_sorted = song_weights.most_common()

        for song_pair in song_weights_sorted:
            if len(rec_song_list) == 100:
                return rec_song_list
            song = song_pair[0]
            if (song not in my_songs) and (song not in rec_song_list):
                rec_song_list.append(song)

        for i in range(len(sorted_list)):
            cur_playlist = song_sets[sorted_list[i][1]]
            for song in cur_playlist:
                if len(rec_song_list) == 100:
                    return rec_song_list
                if (song not in my_songs) and (song not in rec_song_list):
                    rec_song_list.append(song)


    def _get_tag_recommends(self, tag_sets, my_tags, sorted_list):
        rec_tag_list = list()
        weight = []
        tag_weights = Counter()
        cnt = 0
        for i in range(30):
            weight.append(sorted_list[i][0])

        for i in range(30):
            if sorted_list[i][0] == 0:
                break
            cur_taglist = tag_sets[sorted_list[i][1]]
            for tag in cur_taglist:
                if tag not in my_tags:
                    tag_weights[tag] += weight[i]

        tag_weights_sorted = tag_weights.most_common()

        for tag_pair in tag_weights_sorted:
            if len(rec_tag_list) == 10:
                return rec_tag_list
            tag = tag_pair[0]
            if (tag not in my_tags) and (tag not in rec_tag_list):
                rec_tag_list.append(tag)

        for i in range(len(sorted_list)):
            cur_playlist_tags = tag_sets[sorted_list[i][1]]
            for tag in cur_playlist_tags:
                if len(rec_tag_list) == 10:
                    return rec_tag_list
                if (tag not in my_tags) and (tag not in rec_tag_list):
                    rec_tag_list.append(tag)


    def _generate_answers(self, song_meta_json, train, questions):
        song_meta = {int(song["id"]): song for song in song_meta_json}
        song_sets, tag_sets = self._train_playlist(train)
        song_weighted_graph = self._weighted_graph(train)
        answers = []

        for q in tqdm(questions):
            my_songs = q['songs']
            my_tags = q['tags']
            my_artists = set()
            my_genres = set()
            for song in my_songs:
                cur_artists = song_meta[song]['artist_id_basket']
                for artist in cur_artists:
                    my_artists.add(artist)
                cur_genres = song_meta[song]['song_gn_dtl_gnr_basket']
                for genre in cur_genres:
                    my_genres.add(genre)

            cnt = 0
            sorted_list = []
            for song_set in song_sets:
                intersect_num = 0
                for song in my_songs:
                    if song in song_set:
                        intersect_num += 4
                for tag in my_tags:
                    if tag in tag_sets[cnt]:
                        intersect_num += 6
                sorted_list.append([intersect_num, cnt])
                cnt += 1

            sorted_list.sort(key=lambda x: x[0], reverse=True)
            #rec_song_list = self._get_song_recommends(song_sets, my_songs, sorted_list, my_artists, my_genres, song_meta)
            rec_song_list = self._get_weighted_graph_song_recommends(my_songs,song_weighted_graph)

            rec_tag_list = self._get_tag_recommends(tag_sets, my_tags, sorted_list)

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
        song_meta_json = load_json(song_meta_fname)

        print("Loading train file...")
        train_data = load_json(train_fname)

        print("Loading question file...")
        questions = load_json(question_fname)

        print("Writing answers...")
        answers = self._generate_answers(song_meta_json, train_data, questions)
        write_json(answers, "results/results.json")


if __name__ == "__main__":
    fire.Fire(GenreMostPopular)
