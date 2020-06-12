# -*- coding: utf-8 -*-
from collections import Counter

import fire
from tqdm import tqdm

from arena_util import load_json
from arena_util import write_json
from arena_util import remove_seen
from arena_util import most_popular
from datetime import datetime

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


    def _train_playlist(self, train):
        tag_lists = list()
        song_lists = list()

        tag_to_indexes = dict()
        song_to_indexes = dict()

        cnt = 0
        for t in train:
            tag_lists.append(set(t['tags']))
            song_lists.append(set(t['songs']))

            for tag in t['tags']:
                if tag not in tag_to_indexes.keys():
                    tag_to_indexes[tag] = set()
                tag_to_indexes[tag].add(cnt)
            for song in t['songs']:
                if song not in song_to_indexes.keys():
                    song_to_indexes[song] = set()
                song_to_indexes[song].add(cnt)

            cnt += 1

        return song_lists, tag_lists, song_to_indexes, tag_to_indexes


    def _get_song_recommends(self, song_sets, my_songs, sorted_list, my_artists, my_genres, song_meta, cur_date):
        rec_song_list = list()
        weight = []
        song_weights = Counter()

        for i in range(min(len(sorted_list), 20)):
            weight.append(sorted_list[i][1])

        for i in range(min(len(sorted_list), 20)):
            cur_playlist = song_sets[sorted_list[i][0]]
            for song in cur_playlist:
                if song not in my_songs:
                    song_date = song_meta[song]['issue_date']
                    try:
                        song_date = datetime.strptime(song_date, '%Y%m%d')
                    except Exception:
                        try:
                            song_date = datetime.strptime(song_date[:6], '%Y%m')
                        except Exception:
                            try:
                                song_date = datetime.strptime(song_date[:4], '%Y')
                            except Exception:
                                song_date = datetime.strptime('1900', '%Y')

                    if song_date > cur_date:
                        continue

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
            cur_playlist = song_sets[sorted_list[i][0]]
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
        for i in range(min(len(sorted_list), 30)):
            weight.append(sorted_list[i][1])

        for i in range(min(len(sorted_list), 30)):
            if sorted_list[i][1] == 0:
                break
            cur_taglist = tag_sets[sorted_list[i][0]]
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
            cur_playlist_tags = tag_sets[sorted_list[i][0]]
            for tag in cur_playlist_tags:
                if len(rec_tag_list) == 10:
                    return rec_tag_list
                if (tag not in my_tags) and (tag not in rec_tag_list):
                    rec_tag_list.append(tag)

    def is_in(self, val, sets):
        for cur_val in sets:
            if (val == cur_val) or ((len(val) > 3) and (val in cur_val)) or ((len(cur_val) > 3) and (cur_val in val)):
                return True
        return False


    def _generate_answers(self, song_meta_json, train, questions):
        song_meta = {int(song["id"]): song for song in song_meta_json}
        song_mp_counter, song_mp = most_popular(train, "songs", 200)
        tag_mp_counter, tag_mp = most_popular(train, "tags", 100)
        song_mp_per_genre = self._song_mp_per_genre(song_meta, song_mp_counter)
        song_sets, tag_sets, song_to_indexes, tag_to_indexes = self._train_playlist(train)

        answers = []

        base_playlist_votes = Counter()
        for i in range(len(train)):
            base_playlist_votes[i] = 0

        for q in tqdm(questions):
            my_songs = q['songs']
            my_tags = q['tags']
            my_artists = set()
            my_genres = set()
            my_title = q['plylst_title']
            cur_date = datetime.strptime(q['updt_date'][:10], '%Y-%m-%d')

            for song in my_songs:
                cur_artists = song_meta[song]['artist_id_basket']
                for artist in cur_artists:
                    my_artists.add(artist)
                cur_genres = song_meta[song]['song_gn_dtl_gnr_basket']
                for genre in cur_genres:
                    my_genres.add(genre)

            playlist_votes = base_playlist_votes.copy()

            for song in my_songs:
                if song in song_to_indexes.keys():
                    for idx in song_to_indexes[song]:
                        playlist_votes[idx] += 4

            for tag in my_tags:
                if tag in tag_to_indexes.keys():
                    for idx in tag_to_indexes[tag]:
                        playlist_votes[idx] += 6
            
            #아래 주석을 풀면 제목도 비교해서 점수줌 => 점수 꽤 오름
            # cnt = 0
            # for tags in tag_sets:
            #     for word in my_title.split(sep=' '):
            #         if self.is_in(word, tags):
            #             playlist_votes[cnt] += 4
            #     cnt += 1

            sorted_list = playlist_votes.most_common()
            sorted_list.sort(key=lambda x: x[1], reverse=True)

            rec_song_list = self._get_song_recommends(song_sets, my_songs, sorted_list, my_artists, my_genres, song_meta, cur_date)
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
