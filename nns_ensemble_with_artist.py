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


visited_percent_list = list()
accurate_percent_list = list()

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

        return song_lists, tag_lists, title_lists

    def _get_song_recommends(self, song_sets, my_songs, sorted_list, my_artists_counter, my_genres_counter, song_meta,
                             cur_date, ans=None):
        rec_song_list = list()
        weight = []
        song_weights = Counter()

        visited_result = set()

        for i in range(30):
            weight.append(sorted_list[i][0])

        for i in range(30):
            if sorted_list[i][0] == 0:
                break
            cur_playlist = song_sets[sorted_list[i][1]]

            for song in cur_playlist:
                if ans is not None:
                    if song in ans['songs']:
                        visited_result.add(song)

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
                    cur_artists = song_meta[song]['artist_id_basket']

                    for artist in cur_artists:
                        if artist in my_artists_counter:
                            song_weights[song] += weight[i] * (my_artists_counter[artist]) / (
                                sum(my_artists_counter.values()))
                            break

                    cur_genres = song_meta[song]['song_gn_dtl_gnr_basket']
                    tot_num = len(cur_genres)
                    matched_num = 0
                    for genre in cur_genres:
                        if genre in my_genres_counter:
                            matched_num += my_genres_counter[genre]
                    if matched_num:
                        # w = int((matched_num / tot_num)*(weight[i] // 2))
                        song_weights[song] += (matched_num / sum(my_genres_counter.values())) * weight[i]

        song_weights_sorted = song_weights.most_common()

        for song_pair in song_weights_sorted:
            if len(rec_song_list) == 100:
                if ans is not None:
                    visited_percent = len(visited_result) / len(ans['songs'])
                    visited_percent_list.append(visited_percent)

                    found_cnt = 0
                    for song in rec_song_list:
                        if song in ans['songs']:
                            found_cnt += 1

                    found_percent = 0
                    if len(visited_result) != 0:
                        found_percent = found_cnt / len(visited_result)

                    accurate_percent_list.append(found_percent)
                return rec_song_list
            song = song_pair[0]
            if (song not in my_songs) and (song not in rec_song_list):
                rec_song_list.append(song)

        for i in range(len(sorted_list)):
            cur_playlist = song_sets[sorted_list[i][1]]
            for song in cur_playlist:
                if len(rec_song_list) == 100:
                    if ans is not None:
                        visited_percent = len(visited_result) / len(ans['songs'])
                        visited_percent_list.append(visited_percent)

                        found_cnt = 0
                        for song in rec_song_list:
                            if song in ans['songs']:
                                found_cnt += 1

                        found_percent = 0
                        if len(visited_result) != 0:
                            found_percent = found_cnt / len(visited_result)

                        accurate_percent_list.append(found_percent)
                    return rec_song_list
                if (song not in my_songs) and (song not in rec_song_list):
                    rec_song_list.append(song)

    def _get_tag_recommends(self, tag_sets, my_tags, sorted_list, ans=None):
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

    def _generate_answers(self, song_meta_json, train, questions, ans=None, p_idx=0, return_dict=None):
        if return_dict is None:
            return_dict = dict()

        song_meta = {int(song["id"]): song for song in song_meta_json}
        song_sets, tag_sets, title_lists = self._train_playlist(train)

        answers = []

        for q in tqdm(questions):
        # for q in questions:
            cur_ans = None
            if ans is not None:
                for c_ans in ans:
                    if c_ans['id'] == q['id']:
                        cur_ans = c_ans
                        break

            my_songs = q['songs']
            my_tags = q['tags']
            cur_date = datetime.strptime(q['updt_date'][:10], '%Y-%m-%d')
            tag_only = False
            if len(my_songs) == 0 and len(my_tags) != 0:
                tag_only = True

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
                play_list_score = 0

                songs_score = 0
                for song in my_songs:
                    if song in song_set:
                        songs_score += 1

                if len(my_songs) != 0:
                    # 0.001 15가 best
                    songs_score = songs_score / math.log(1 + len(song_set))

                play_list_score += songs_score * 15

                tag_score = 0
                for tag_q in my_tags:


                    for tag_t in tag_sets[idx]:
                        if tag_q in tag_t or tag_t in tag_q:
                            if tag_t == tag_q:
                                tag_score += 6
                                if tag_only:
                                    break
                            else:
                                if not tag_only:
                                    tag_score += 2

                if len(tag_sets[idx]) != 0:
                    tag_score = tag_score / math.log(1 + len(tag_sets[idx]))

                play_list_score += tag_score

                title_score = 0
                for word in my_title:
                    if word in title_lists[idx]:
                        title_score += 1
                play_list_score += 3 * title_score
                sorted_list.append([play_list_score, idx])

            sorted_list.sort(key=lambda x: x[0], reverse=True)
            rec_song_list = self._get_song_recommends(song_sets, my_songs, sorted_list, my_artists_counter,
                                                      my_genres_counter, song_meta, cur_date, ans=cur_ans)
            rec_tag_list = self._get_tag_recommends(tag_sets, my_tags, sorted_list, ans=cur_ans)

            if len(rec_song_list) != 100:
                print(f'song sz : {len(rec_song_list)}')

            if len(rec_tag_list) != 10:
                print(f'tag sz : {len(rec_tag_list)}')

            answers.append({
                "id": q["id"],
                "songs": rec_song_list,
                "tags": rec_tag_list
            })
        return_dict[p_idx] = answers
        if ans is not None:
            avg_visited_percent_list = 0.0
            avg_accurate_percent_list = 0.0
            sum_percent = 0.0
            sum_accurate_percent = 0.0
            actual_cnt = 0
            for idx, per in enumerate(visited_percent_list):
                sum_percent += per
                if (per != 0) or (per != 0.0):
                    actual_cnt += 1
                    sum_accurate_percent += accurate_percent_list[idx]

            avg_visited_percent_list = sum_percent / len(visited_percent_list)
            if actual_cnt != 0:
                avg_accurate_percent_list = sum_accurate_percent/actual_cnt

            print(f'avg visited song percent : {avg_visited_percent_list}')
            print(f'avg found song in visited songs percent : {avg_accurate_percent_list}')

            from matplotlib import pyplot as plt

            plt.hist(visited_percent_list, alpha=0.5, bins=20, label='visited_percent')
            plt.hist(accurate_percent_list, alpha=0.5, bins=20, label='accurate_percent')
            plt.legend(loc='upper right')
            plt.show()

        return answers

    def run(self, song_meta_fname, train_fname, question_fname, train_ans_fname=None):
        print("Loading song meta...")
        song_meta_json = load_json(song_meta_fname)

        print("Loading train file...")
        train_data = load_json(train_fname)

        print("Loading question file...")
        questions = load_json(question_fname)

        print("Loading question file...")
        ans = None
        if train_ans_fname != None:
            ans = load_json(train_ans_fname)

        print("Writing answers...")
        answers = self._generate_answers(song_meta_json, train_data, questions, ans)
        write_json(answers, "results/results.json")


if __name__ == "__main__":
    fire.Fire(GenreMostPopular)
