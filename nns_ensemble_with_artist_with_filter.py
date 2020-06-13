# -*- coding: utf-8 -*-
from collections import Counter

import fire
from tqdm import tqdm

from solve_others import solve_others

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

    class Condition:
        NOTHING = "NOTHING"
        TITLE_ONLY = "TITLE_ONLY"
        TAG_ONLY = "TAG_ONLY"
        SONG_ONLY = "SONG_ONLY"
        TITLE_TAG = "TITLE_TAG"
        TITLE_SONG = "TITLE_SONG"
        TAG_SONG = "TAG_SONG"
        ALL = "ALL"

    def _generate_answers(self, song_meta_json, train, questions):
        # title tags songs
        condition = [[["" for col in range(2)] for row in range(2)] for depth in range(2)]
        condition[0][0][0] = self.Condition.NOTHING
        condition[1][0][0] = self.Condition.TITLE_ONLY
        condition[0][1][0] = self.Condition.TAG_ONLY
        condition[0][0][1] = self.Condition.SONG_ONLY
        condition[1][1][0] = self.Condition.TITLE_TAG
        condition[1][0][1] = self.Condition.TITLE_SONG
        condition[0][1][1] = self.Condition.TAG_SONG
        condition[1][1][1] = self.Condition.ALL


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
            my_title = q['plylst_title']
            cur_date = datetime.strptime(q['updt_date'][:10], '%Y-%m-%d')

            my_songs_len = 1 if len(my_songs) > 0 else 0
            my_tags_len = 1 if len(my_tags) > 0 else 0
            my_title_len = 1 if len(my_title) > 0 else 0

            # title tags songs
            my_condition = condition[my_title_len][my_tags_len][my_songs_len]

            if my_condition == self.Condition.SONG_ONLY:
                rec_song_list, rec_tag_list = solve_others(song_sets, tag_sets, song_meta, my_songs, my_tags, cur_date,
                                                           base_playlist_votes, song_to_indexes, tag_to_indexes)
                # rec_song_list, rec_tag_list = \
                #     solve_song_only(song_sets, tag_sets, title_lists, song_meta, my_songs, my_tags, my_title,cur_date)
            elif my_condition == self.Condition.TAG_SONG:
                rec_song_list, rec_tag_list = solve_others(song_sets, tag_sets, song_meta, my_songs, my_tags, cur_date,
                                                           base_playlist_votes, song_to_indexes, tag_to_indexes)
                # rec_song_list, rec_tag_list = solve_song_tag(song_sets, tag_sets, title_lists,
                #                                              song_meta, my_songs, my_tags, my_title,cur_date)
            elif my_condition == self.Condition.TITLE_TAG:
                rec_song_list, rec_tag_list = solve_others(song_sets, tag_sets, song_meta, my_songs, my_tags, cur_date,
                                                           base_playlist_votes, song_to_indexes, tag_to_indexes)
                # rec_song_list, rec_tag_list = solve_title_tag(song_sets, tag_sets, title_lists,
                #                                               song_meta, my_songs, my_tags, my_title,cur_date)
            elif my_condition == self.Condition.TITLE_ONLY:
                rec_song_list, rec_tag_list = solve_others(song_sets, tag_sets, song_meta, my_songs, my_tags, cur_date,
                                                           base_playlist_votes, song_to_indexes, tag_to_indexes)
                # rec_song_list, rec_tag_list = solve_title_only(song_sets, tag_sets, title_lists,
                #                                                song_meta, my_songs, my_tags, my_title,cur_date)
            elif my_condition == self.Condition.TAG_ONLY:
                rec_song_list, rec_tag_list = solve_others(song_sets, tag_sets, song_meta, my_songs, my_tags, cur_date,
                                                           base_playlist_votes, song_to_indexes, tag_to_indexes)
                # rec_song_list, rec_tag_list = solve_tag_only(song_sets, tag_sets, title_lists,
                #                                              song_meta, my_songs, my_tags, my_title,cur_date)
            elif my_condition == self.Condition.TITLE_SONG:
                rec_song_list, rec_tag_list = solve_others(song_sets, tag_sets, song_meta, my_songs, my_tags, cur_date,
                                                           base_playlist_votes, song_to_indexes, tag_to_indexes)
                # rec_song_list, rec_tag_list = solve_title_song(song_sets, tag_sets, title_lists,
                #                                                song_meta, my_songs, my_tags, my_title,cur_date)
            elif my_condition == self.Condition.ALL:
                rec_song_list, rec_tag_list = solve_others(song_sets, tag_sets, song_meta, my_songs, my_tags, cur_date,
                                                           base_playlist_votes, song_to_indexes, tag_to_indexes)
                #rec_song_list, rec_tag_list = solve_all()
                # nothing
            else:
                rec_song_list, rec_tag_list = solve_others(song_sets, tag_sets, song_meta, my_songs, my_tags, cur_date,
                                                           base_playlist_votes, song_to_indexes, tag_to_indexes )


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
