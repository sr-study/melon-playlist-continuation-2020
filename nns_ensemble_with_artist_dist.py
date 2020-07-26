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
from enum import Enum, auto

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


class ProblemType(Enum):
    SONG_ONLY = auto()
    SONG_TAG = auto()
    TAG_TITLE = auto()
    TITLE_ONLY = auto()
    ELSE = auto()


def get_problem_type(songs, tags, titles):
    # song
    if len(songs) != 0 and len(tags) == 0 and len(titles) == 0:
        return ProblemType.SONG_ONLY
    # song tag
    if len(songs) != 0 and len(tags) != 0 and len(titles) == 0:
        return ProblemType.SONG_TAG
    # tag title
    if len(songs) == 0 and len(tags) != 0 and len(titles) != 0:
        return ProblemType.TAG_TITLE
    # title
    if len(songs) == 0 and len(tags) == 0 and len(titles) != 0:
        return ProblemType.TITLE_ONLY
    return ProblemType.ELSE

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

        tag_to_indexes = dict()
        song_to_indexes = dict()
        title_to_indexes = dict()

        train = sorted(train, key=lambda x: x['id'])
        for cnt, t in enumerate(train):
            # print(t)
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

            words = get_words(t['plylst_title'])
            for word in words:
                if word not in title_to_indexes.keys():
                    title_to_indexes[word] = set()
                title_to_indexes[word].add(cnt)

            title_lists.append(words)
            for word in words:
                most_popular_words[word] += 1
            cur_date = datetime.strptime(t['updt_date'][:10], '%Y-%m-%d')
            year_month_score = (cur_date.year * 12) + (cur_date.month - 1)
            year_month_lists.append(year_month_score)

        return song_lists, tag_lists, song_to_indexes, tag_to_indexes, title_to_indexes, title_lists, year_month_lists

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
        song_sets, tag_sets, song_to_indexes, tag_to_indexes, title_to_indexes, title_lists, year_month_lists = self._train_playlist(train)

        base_playlist_scores = dict()
        for i in range(len(train)):
            base_playlist_scores[i] = 0.0

        # start koo
        artist_id = dict()
        artist_name = dict()
        artist_mopop_tmp = dict()
        artist_mopop = dict()
        artist_name_cnt = list()
        artist_name_cnt_tmp = list()
        artist_name_cnt_threshold = 1000

        for i in tqdm(song_meta_json):
            if len(i['artist_id_basket']) == len(i['artist_name_basket']):
                for idx, name in enumerate(i['artist_name_basket']):
                    artist_id[i['artist_id_basket'][idx]] = name.lower()
                    if len(name) > 5 and name[-1] == ')':
                        for p in range(len(name)):
                            if name[p] == '(':
                                if name[p - 1] == ' ':
                                    artist_name[name[:p - 1].lower()] = i['artist_id_basket'][idx]
                                else:
                                    artist_name[name[:p].lower()] = i['artist_id_basket'][idx]
                                artist_name[name[p + 1:-1].lower()] = i['artist_id_basket'][idx]
                                break
                    artist_name[name.lower()] = i['artist_id_basket'][idx]
                    if name.lower() not in artist_mopop_tmp:
                        artist_mopop_tmp[name.lower()] = list()
                    artist_mopop_tmp[name.lower()].append(i['id'])

        for i in tqdm(questions + train):
            for s in i['songs']:
                for name in song_meta_json[s]['artist_name_basket']:
                    artist_name_cnt_tmp.append(name.lower())
                    if name.lower() in artist_mopop_tmp:
                        artist_mopop_tmp[name.lower()].append(s)

        for name, cnt in tqdm(artist_mopop_tmp.items()):
            cnt = Counter(cnt)
            tmp_list = list()
            for key, value in cnt.items():
                tmp_list.append((key, value))
            cnt = sorted(tmp_list, reverse=True, key=lambda x: x[1])
            tmp_list = list()
            for v in cnt:
                tmp_list.append(v[0])
            artist_mopop[name] = tmp_list

        artist_name_cnt_tmp = Counter(artist_name_cnt_tmp)
        for key, value in artist_name_cnt_tmp.items():
            if value >= artist_name_cnt_threshold and len(key) > 1:
                if len(key) > 5 and key[-1] == ')':
                    for p in range(len(key)):
                        if key[p] == '(':
                            if key[p - 1] == ' ':
                                artist_name_cnt.append(key[:p - 1].lower())
                            else:
                                artist_name_cnt.append(key[:p].lower())
                            artist_name_cnt.append(key[p + 1:-1].lower())
                            break
                artist_name_cnt.append(key.lower())

        except_list = ['클래식', '라디', '구름', '노을','이루','이브','el','자장가','40','동요','다운','지나','one',
                       '새벽감성','제이','잠들기전','잔잔한 피아노','blue','테이','디바','팀','가인','유희열','오르골'
                       ,'max','보니','healing','아재','루나','yg','ja']
        # end koo

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
            my_title_2 = q['plylst_title']
            for word in my_title:
                most_popular_words[word] += 1
            my_artists_counter = Counter()
            my_genres_counter = Counter()
            for song in my_songs:
                cur_artists = song_meta[song]['artist_id_basket']
                my_artists_counter.update(cur_artists)

                cur_genres = song_meta[song]['song_gn_dtl_gnr_basket']
                my_genres_counter.update(cur_genres)

            ###################################################
            song_size = 0
            singer_list = list()
            answer_list = list()
            singer_id_list = list()
            for song in my_songs:
                song_size += 1
                for name in song_meta[song]['artist_name_basket']:
                    singer_list.append(name.lower())
                for sid in song_meta[song]['artist_id_basket']:
                    singer_id_list.append(sid)
            singer_list = Counter(singer_list)
            for key, value in singer_list.items():
                if song_size >= 5 and song_size * 0.8 <= value:
                    if key.lower() in artist_mopop:
                        answer_list = artist_mopop[key.lower()].copy()

            if len(my_title_2) > 1:
                for name in artist_name_cnt:
                    if len(name) > 1 and (name.lower() in my_title_2.lower()) and (name.lower() not in except_list):
                        if len(singer_id_list) > 0 and (artist_name[name] not in singer_id_list):
                            continue
                        # print(name, my_title)
                        for song in artist_mopop[artist_id[artist_name[name.lower()]]]:
                            answer_list.append(song)
            ###################################################
            sorted_list = []
            play_list_scores = base_playlist_scores.copy()


            problem_type = get_problem_type(my_songs, my_tags, my_title)

            song_knn = 10
            tag_knn = 30
            song_weight = 15
            tag_weight = 6
            title_weight = 3
            penalty_alpha = 1

            if problem_type == ProblemType.SONG_ONLY:
                song_weight = 12
                tag_weight = 6
                title_weight = 3
                song_knn = 10
                tag_knn = 30
            elif problem_type == ProblemType.SONG_TAG:
                song_weight = 15
                tag_weight = 6
                title_weight = 3
                song_knn = 10
                tag_knn = 30
            elif problem_type == ProblemType.TAG_TITLE:
                song_weight = 15
                tag_weight = 6
                title_weight = 3
                song_knn = 10
                tag_knn = 30
            elif problem_type == ProblemType.TITLE_ONLY:
                song_weight = 15
                tag_weight = 6
                title_weight = 5
                song_knn = 30
                tag_knn = 30
            else:
                song_weight = 15
                tag_weight = 6
                title_weight = 3
                song_knn = 10
                tag_knn = 30

            for song in my_songs:
                if song in song_to_indexes.keys():
                    for idx in song_to_indexes[song]:
                        play_list_scores[idx] += (song_weight / (math.log(len(song_sets[idx]) + 1)))

            for tag in my_tags:
                if tag in tag_to_indexes.keys():
                    for idx in tag_to_indexes[tag]:
                        play_list_scores[idx] += (tag_weight / (math.log(len(tag_sets[idx]) + 1)))

            for word in my_title:
                if word in title_to_indexes.keys():
                    for idx in title_to_indexes[word]:
                        play_list_scores[idx] += (title_weight / (math.log(len(title_lists[idx]) + 1)))

            for idx, t in enumerate(year_month_lists):
                trend_penalty = pow(abs(year_month_lists[idx] - year_month_score), 2) * (1e-3)
                play_list_scores[idx] -= (penalty_alpha * trend_penalty)

            for k, v in play_list_scores.items():
                sorted_list.append((v, k))

            sorted_list.sort(key=lambda x: (x[0], x[1]), reverse=True)

            rec_song_list = self._get_song_recommends(song_sets, my_songs, sorted_list, my_artists_counter,
                                                      my_genres_counter, song_meta, cur_date, song_knn)
            rec_tag_list = self._get_tag_recommends(tag_sets, my_tags, sorted_list, tag_knn)

            real_answer = list()
            for s in answer_list:
                if (s not in my_songs) and (s not in real_answer) and q['updt_date'] > song_meta_json[s]['issue_date']:
                    real_answer.append(s)
            for s in rec_song_list:
                if (s not in my_songs) and (s not in real_answer):
                    real_answer.append(s)
            real_answer = real_answer[:100]

            more_search = 3
            if len(rec_song_list) != 100:
                print(f'song sz : {len(real_answer)}')
            if len(rec_tag_list) != 10:
                print(f'tag sz : {len(rec_tag_list)}')

            answers.append({
                "id": q["id"],
                "songs": real_answer,
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
