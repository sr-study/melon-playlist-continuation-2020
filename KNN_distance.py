# -*- coding: utf-8 -*-
from collections import Counter

import fire
from tqdm import tqdm
import math
from arena_util import load_json
from arena_util import write_json
from datetime import datetime
from arena_util import remove_seen
from arena_util import most_popular


class KNN_distance:
    def __init__(self):
        self.song_lists = []

        self.title_lists = []
        self.tag_lists = []

        self.artists_counter = Counter()
        self.dtl_genres_counter = Counter()
        self.genres_counter = Counter()
        self.album_counter = Counter()
        self.artists_lists = []
        self.detail_gen_list = []
        self.gen_list = []
        self.album_list = []

        self.artists_lists_size = []
        self.detail_gen_list_size  = []
        self.gen_list_size  = []
        self.album_list_size  = []

        self.album_size = 0
        self.dtl_genre_size = 0
        self.genres_size = 0
        self.artist_size = 0

    def _song_mp_per_genre(self, song_meta, global_mp):
        res = {}

        for sid, song in song_meta.items():
            for genre in song['song_gn_gnr_basket']:
                res.setdefault(genre, []).append(sid)

        for genre, sids in res.items():
            res[genre] = Counter({k: global_mp.get(int(k), 0) for k in sids})
            res[genre] = [k for k, v in res[genre].most_common(200)]

        return res

    def dot(self, dict_1, dict_2):
        total = dict_1 & dict_2
        dot_product = sum(dict_1[key] * dict_2[key] for i,key in enumerate(total))
        return dot_product

    def cosine_sim(self, a,b):

        if len(a) ==0 or len(b)==0:
            return 0

        return self.dot(a,b)/(math.sqrt(self.dot(a,a))*math.sqrt(self.dot(b,b)))

    def _train_playlist(self, train, song_meta):



        for t in train:
            artists_counter = Counter()
            dtl_genres_counter = Counter()
            genres_counter = Counter()
            album_counter = Counter()

            for each_song in t['songs']:
                artists_counter.update(song_meta[each_song]['artist_id_basket'])
                dtl_genres_counter.update(song_meta[each_song]['song_gn_dtl_gnr_basket'])
                genres_counter.update(song_meta[each_song]['song_gn_gnr_basket'])
                album_counter.update([song_meta[each_song]['album_id']])


            self.tag_lists.append(set(t['tags']))
            self.song_lists.append(set(t['songs']))
            self.title_lists.append(t['plylst_title'].split(' '))

            self.artists_lists.append(artists_counter)
            self.detail_gen_list.append(dtl_genres_counter)
            self.gen_list.append(genres_counter)
            self.album_list.append(album_counter)

            self.artists_lists_size.append(math.sqrt(self.dot(artists_counter,artists_counter)))
            self.detail_gen_list_size.append(math.sqrt(self.dot(dtl_genres_counter,dtl_genres_counter)))
            self.gen_list_size.append(math.sqrt(self.dot(genres_counter,genres_counter)))
            self.album_list_size.append(math.sqrt(self.dot(album_counter,album_counter)))







    def _get_song_recommends(self, song_sets, my_songs, sorted_list,song_meta,cur_date):
        rec_song_list = list()
        weight = []
        song_weights = Counter()

        K = 20
        for i in range(K):
            idx =sorted_list[i][1]

            artist_score = 0
            gnl_score = 0
            dtl_gnl_score = 0
            album_score = 0

            if self.artists_lists_size[idx] != 0 and self.artist_size != 0:
                artist_score = self.dot(self.artists_counter, self.artists_lists[idx]) / self.artists_lists_size[
                    idx] / self.artist_size
            if self.gen_list_size[idx] != 0 and self.genres_size != 0:
                gnl_score = self.dot(self.genres_counter, self.gen_list[idx]) / self.gen_list_size[idx] / self.genres_size
            if self.detail_gen_list_size[idx] != 0 and self.dtl_genre_size != 0:
                dtl_gnl_score = self.dot(self.dtl_genres_counter, self.detail_gen_list[idx]) / self.detail_gen_list_size[
                    idx] / self.dtl_genre_size

            if self.artists_lists_size[idx] != 0 and self.album_size != 0:
                album_score = self.dot(self.album_counter, self.album_list[idx]) / self.artists_lists_size[idx] / self.album_size
            score = sorted_list[i][0] *( 1* dtl_gnl_score + 1 * gnl_score + 1 * album_score + 1 * artist_score)
            weight.append(score)

        for i in range(K):
            if sorted_list[i][0] == 0:
                break
            cur_playlist = song_sets[sorted_list[i][1]]


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

                        
                if song not in my_songs:
                    song_weights[song] += weight[i]




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
        self._train_playlist(train, song_meta)

        answers = []



        for q in tqdm(questions):
            my_songs = q['songs']
            my_tags = q['tags']
            cur_date = datetime.strptime(q['updt_date'][:10], '%Y-%m-%d')


            my_title = q['plylst_title'].split(' ')
            artists_counter = Counter()
            dtl_genres_counter = Counter()
            genres_counter = Counter()
            album_counter = Counter()
            for song in my_songs:

                artists_counter.update( song_meta[song]['artist_id_basket'])
                dtl_genres_counter.update(song_meta[song]['song_gn_dtl_gnr_basket'])
                genres_counter.update(song_meta[song]['song_gn_gnr_basket'])
                album_counter.update([song_meta[song]['album_id']])

            self.album_size = math.sqrt(self.dot(album_counter,album_counter))
            self.dtl_genre_size = math.sqrt(self.dot(dtl_genres_counter,dtl_genres_counter))
            self.genres_size =  math.sqrt(self.dot(genres_counter,genres_counter))
            self.artist_size = math.sqrt(self.dot(artists_counter,artists_counter))

            sorted_list = []

            for idx, song_set in enumerate(self.song_lists):
                song_score = 0
                for song in my_songs:
                    if song in song_set:
                        song_score += 1

                if len(my_songs)!= 0:
                    song_score= song_score/len(my_songs)/len(song_set)

                tag_score = 0
                for tag_q in my_tags:
                    for tag_t in self.tag_lists[idx]:
                        if tag_q in tag_t or tag_t in tag_q:
                            if tag_t ==tag_q:
                                tag_score += 1
                            else:
                                tag_score += 0.5

                if len(my_tags)!= 0:
                    tag_score= tag_score/len(my_tags)/len(self.tag_lists[idx])

                tilte_score =0
                for word_q in my_title:
                     for word_t in self.title_lists[idx]:
                        if word_q in word_t or word_t in word_q:
                            if word_q == word_t:
                                tilte_score += 1
                            else:
                                tilte_score += 0.5
                if len(my_title)!= 0:
                    tilte_score= tilte_score/len(my_title)/len(self.title_lists[idx])




                # if self.artists_lists_size[idx]!= 0 and artist_size!=0 :
                #     artist_score = self.dot(artists_counter,self.artists_lists[idx])/self.artists_lists_size[idx]/artist_size
                # if self.gen_list_size[idx] != 0 and genres_size != 0:
                #     gnl_score = self.dot(genres_counter, self.gen_list[idx])/self.gen_list_size[idx]/genres_size
                # if self.detail_gen_list_size[idx] != 0 and dtl_genre_size != 0:
                #     dtl_gnl_score = self.dot(dtl_genres_counter, self.detail_gen_list[idx])/self.detail_gen_list_size[idx]/dtl_genre_size
                #
                # if self.artists_lists_size[idx] != 0 and album_size != 0:
                #     album_score  = self.dot(album_counter,self.album_list[idx]) /self.artists_lists_size[idx] / album_size



                score = 0*tilte_score + 0*tag_score + 3*song_score

                sorted_list.append([score, idx])


            sorted_list.sort(key=lambda x: x[0], reverse=True)



            rec_song_list = self._get_song_recommends(self.song_lists, my_songs, sorted_list,  song_meta, cur_date)
            rec_tag_list = self._get_tag_recommends(self.tag_lists, my_tags, sorted_list)

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
    fire.Fire(KNN_distance)
