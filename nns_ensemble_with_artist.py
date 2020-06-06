# -*- coding: utf-8 -*-
from collections import Counter

import fire
from tqdm import tqdm

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


    def _train_playlist(self, train):
        tag_lists = []
        song_lists = []
        title_lists = []
        for t in train:
            tag_lists.append(set(t['tags']))
            song_lists.append(set(t['songs']))
            title_lists.append(t['plylst_title'].split(' '))

        return song_lists, tag_lists,title_lists


    def _get_song_recommends(self, song_sets, my_songs, sorted_list, my_artists_counter, my_genres_counter, song_meta):
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


                    for artist in cur_artists:
                        if artist in my_artists_counter:
                            song_weights[song] += (weight[i] / 4) * (my_artists_counter[artist])/(sum(my_artists_counter.values()))
                            break


                    cur_genres = song_meta[song]['song_gn_dtl_gnr_basket']
                    tot_num = len(cur_genres)
                    matched_num = 0
                    for genre in cur_genres:
                        if genre in my_genres_counter:
                            matched_num += my_genres_counter[genre]
                    if matched_num:
                        #w = int((matched_num / tot_num)*(weight[i] // 2))
                        song_weights[song] += ( matched_num/ (sum(my_genres_counter.values())))*(weight[i] / 5)

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
        song_sets, tag_sets, title_lists = self._train_playlist(train)

        answers = []

        for q in tqdm(questions):
            my_songs = q['songs']
            my_tags = q['tags']
            my_title = q['plylst_title'].split(' ')
            my_artists_counter = Counter()
            my_genres_counter = Counter()
            for song in my_songs:
                cur_artists = song_meta[song]['artist_id_basket']
                my_artists_counter.update(cur_artists)

                cur_genres = song_meta[song]['song_gn_dtl_gnr_basket']
                my_genres_counter.update(cur_genres)


            sorted_list = []

            for idx, song_set in enumerate(song_sets):
                intersect_num = 0
                for song in my_songs:
                    if song in song_set:
                        intersect_num += 4

                for tag_q in my_tags:
                    chk = False
                    for tag_t in tag_sets[idx]:
                        ## == 에서 in 으로 바꿔었다가 다시 == 으로 바꾸었다.
                        if tag_q == tag_t:
                            chk = True
                            break
                    if chk:
                        intersect_num += 6

                for word in my_title:
                    if word in title_lists[idx]:
                        intersect_num += 10

                sorted_list.append([intersect_num, idx])


            sorted_list.sort(key=lambda x: x[0], reverse=True)
            rec_song_list = self._get_song_recommends(song_sets, my_songs, sorted_list, my_artists_counter, my_genres_counter, song_meta)
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
