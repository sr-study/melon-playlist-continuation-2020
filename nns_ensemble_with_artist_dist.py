# -*- coding: utf-8 -*-
from collections import Counter

import fire
from tqdm import tqdm
import math
from arena_util import load_json
from arena_util import write_json
from datetime import datetime
import pandas as pd
import re

most_popular_words = Counter()
most_intersect_words = Counter()
filtered_word = []#'노래', '좋은', '음악', '듣는', '모음', '곡', '플레이리스트']
# filtered_word = ['노래', '좋은', '음악', '듣는', '모음', '듣기', '노래들', '때', '날', '곡', '플레이리스트', '음악들', '이', '듣고', '있는', '내', 'in', 'vol2', '후에', '좋게'
#                  '명곡', '한', '내가', '곡들', '듣기좋은', '모음집', '그', '더', '요즘', 'music', '추천',
#                  '뮤직', '2', '같은', 'best', '리스트', '1', '하는', '수',
#                  '되는', '좋아하는', 'the', '들어도', '생각나는', '베스트', '듣고싶은', '취향저격', '그리고', '할',
#                  '싶을', '꼭', '오는', '나만', '노래모음',
#                  '나를', '최신곡', '명곡들', '오늘', '나의', '속', '만드는', 'top',
#                  '그냥', 'hot', '없는', '싶을때', '많이', '사운드', '당신을', '함께하는', '잘', '나만의',
#                  '추천곡', '지금', '나는', '띵곡', '딱', '가득한', '너무', '오늘의',
#                  '들어요', '들을', '줄', '않은', '주', '다시', '주는', '마음', '시간', '최신', '다', '가수',
#                  '50', '같이', 'playlist']


def get_words(s: str):
    s = remove_special_chars(s)
    s = remove_incomplete_chars(s)
    s = s.lower()
    return s.split()


def remove_special_chars(s: str):
    pattern = '[^\w\s]'
    replace = ''
    return re.sub(pattern=pattern, repl=replace, string=s)


def remove_incomplete_chars(s: str):
    pattern = '[ㄱ-ㅎㅏ-ㅣ]'
    replace = ''
    return re.sub(pattern=pattern, repl=replace, string=s)

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
        year_month_lists = []
        train = sorted(train, key=lambda x: x['id'])
        for t in train:
            # print(t)
            tag_lists.append(set(t['tags']))
            song_lists.append(set(t['songs']))
            # title_lists.append(t['plylst_title'].split(' '))
            words = get_words(t['plylst_title'])
            title_lists.append(words)
            for word in words:
                most_popular_words[word] += 1
            cur_date = datetime.strptime(t['updt_date'][:10], '%Y-%m-%d')
            year_month_score = (cur_date.year * 12) + (cur_date.month - 1)
            year_month_lists.append(year_month_score)

        return song_lists, tag_lists, title_lists, year_month_lists

    def _get_song_recommends(self, song_sets, my_songs, sorted_list, my_artists_counter, my_genres_counter, song_meta,
                             cur_date, K_NN):
        rec_song_list = list()
        weight = []
        song_weights = Counter()

        for i in range(K_NN):
            weight.append(sorted_list[i][0])

        for i in range(K_NN):
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

                    # aritist score

                    # query play_list artist <-> the each song artist
                    cur_artists = song_meta[song]['artist_id_basket']
                    for artist in cur_artists:
                        if artist in my_artists_counter:
                            song_weights[song] += weight[i] * (my_artists_counter[artist]) / sum(
                                my_artists_counter.values())
                            break

                    # detail ger score

                    # query play_list gen <-> the each song ger

                    cur_genres = song_meta[song]['song_gn_dtl_gnr_basket']
                    tot_num = len(cur_genres)
                    matched_num = 0
                    for genre in cur_genres:
                        if genre in my_genres_counter:
                            matched_num += my_genres_counter[genre]
                    if matched_num:
                        song_weights[song] += weight[i] * (matched_num / sum(my_genres_counter.values()))

        # song_weights_sorted = song_weights.most_common()
        song_weights_sorted = sorted(song_weights.most_common(), key=lambda x: (-x[1], x[0]))

        for song_pair in song_weights_sorted:
            if len(rec_song_list) == 100:
                return rec_song_list
            song = song_pair[0]
            if (song not in my_songs) and (song not in rec_song_list):
                rec_song_list.append(song)

        for i in range(len(sorted_list)):
            cur_playlist = sorted(song_sets[sorted_list[i][1]])
            for song in cur_playlist:
                if len(rec_song_list) == 100:
                    return rec_song_list
                if (song not in my_songs) and (song not in rec_song_list):
                    rec_song_list.append(song)

    def _get_tag_recommends(self, tag_sets, my_tags, sorted_list, K_NN):
        rec_tag_list = list()
        weight = []
        tag_weights = Counter()
        cnt = 0
        for i in range(K_NN):
            weight.append(sorted_list[i][0])

        for i in range(K_NN):
            if sorted_list[i][0] == 0:
                break
            cur_taglist = tag_sets[sorted_list[i][1]]
            for tag in cur_taglist:
                if tag not in my_tags:
                    tag_weights[tag] += weight[i]

        # tag_weights_sorted = tag_weights.most_common()
        tag_weights_sorted = sorted(tag_weights.most_common(), key=lambda x: (-x[1], x[0]))

        for tag_pair in tag_weights_sorted:
            if len(rec_tag_list) == 10:
                return rec_tag_list
            tag = tag_pair[0]
            if (tag not in my_tags) and (tag not in rec_tag_list):
                rec_tag_list.append(tag)

        for i in range(len(sorted_list)):
            cur_playlist_tags = sorted(tag_sets[sorted_list[i][1]])
            for tag in cur_playlist_tags:
                if len(rec_tag_list) == 10:
                    return rec_tag_list
                if (tag not in my_tags) and (tag not in rec_tag_list):
                    rec_tag_list.append(tag)

    def _generate_answers(self, song_meta_json, train, questions, result_df, ans=None, p_idx=0, return_dict=None):
        if return_dict is None:
            return_dict = dict()

        song_meta = {int(song["id"]): song for song in song_meta_json}
        song_sets, tag_sets, title_lists, year_month_lists = self._train_playlist(train)

        answers = []

        for q in tqdm(questions):
            id = q['id']
            my_songs = q['songs']
            my_tags = q['tags']
            cur_date = datetime.strptime(q['updt_date'][:10], '%Y-%m-%d')
            year_month_score = (cur_date.year * 12) + (cur_date.month - 1)

            tag_only = False
            if len(my_songs) == 0 and len(my_tags) != 0:
                tag_only = True

            my_title = get_words(q['plylst_title'])
            for word in my_title:
                most_popular_words[word] += 1
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

                if len(song_set) != 0:
                    songs_score = songs_score / (math.log(len(song_set) + 1))

                play_list_score += 15 * songs_score

                tag_score = 0
                for tag_q in my_tags:
                    for tag_t in tag_sets[idx]:
                        if tag_t == tag_q:
                            tag_score += 1

                if len(tag_sets[idx]) != 0:
                    tag_score = tag_score / (math.log(len(tag_sets[idx]) + 1))
                play_list_score += 6 * tag_score

                title_score = 0
                for word in my_title:
                    if (word in title_lists[idx]) and (word not in filtered_word):
                        most_intersect_words[word] += 1
                        title_score += 1

                if len(title_lists[idx]) != 0:
                    title_score = title_score / (math.log(len(title_lists[idx]) + 1))

                play_list_score += 3 * title_score

                # print(f'before_play_list_score : {play_list_score}')
                trend_penalty = pow(abs(year_month_lists[idx] - year_month_score), 2) * (1e-3)
                play_list_score -= trend_penalty

                # print(f'penalty : {trend_penalty}, after_play_list_score : {play_list_score}')

                sorted_list.append([play_list_score, idx, songs_score, tag_score, title_score])

            sorted_list.sort(key=lambda x: (x[0], x[1]), reverse=True)

            mean_tag = 0
            mean_music = 0
            mean_title = 0
            K_NN = 10
            for i in range(K_NN):
                mean_music += sorted_list[i][2]
                mean_tag += sorted_list[i][3]
                mean_title += sorted_list[i][4]

            result_df.loc[len(result_df)] = [id, mean_music / K_NN, mean_tag / K_NN, mean_title / K_NN]

            # if best_3_mean<1.5:
            #     more_search=1
            rec_song_list = self._get_song_recommends(song_sets, my_songs, sorted_list, my_artists_counter,
                                                      my_genres_counter, song_meta, cur_date, 10)
            rec_tag_list = self._get_tag_recommends(tag_sets, my_tags, sorted_list, 30)

            more_search = 3
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
        # print([pair[0] for pair in most_popular_words.most_common()[:200]])
        # print(most_popular_words.most_common()[:200])
        # print(most_intersect_words.most_common()[:200])
        return answers

    def run(self, song_meta_fname, train_fname, question_fname):
        print("Loading song meta...")
        song_meta_json = load_json(song_meta_fname)

        print("Loading train file...")
        train_data = load_json(train_fname)

        print("Loading question file...")
        questions = load_json(question_fname)

        print("Writing answers...")
        result_df = pd.DataFrame(
            columns=['id', 'means_music_score', 'mean_tag_score', 'mean_title_score'])
        answers = self._generate_answers(song_meta_json, train_data, questions, result_df)
        result_df.to_csv('./arena_data/question_k_score.csv', index=False)

        write_json(answers, "results/results.json")


if __name__ == "__main__":
    fire.Fire(GenreMostPopular)
