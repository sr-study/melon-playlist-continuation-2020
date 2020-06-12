# -*- coding: utf-8 -*-
from collections import Counter

import fire

from solve_song_only import solve_song_only
from solve_tag_only import solve_tag_only
from solve_title_only import solve_title_only
from solve_song_tag import solve_song_tag
from solve_title_tag import solve_title_tag
from solve_title_song import solve_title_song
from solve_others import solve_others
from solve_all import solve_all

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

        return song_lists, tag_lists, title_lists

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
        song_sets, tag_sets, title_lists = self._train_playlist(train)

        answers = []

        for q in tqdm(questions):
            my_songs = q['songs']
            my_tags = q['tags']
            my_title = q['plylst_title'].split(' ')

            my_songs_len = 1 if len(my_songs) > 0 else 0
            my_tags_len = 1 if len(my_tags) > 0 else 0
            my_title_len = 1 if len(q['plylst_title']) > 0 else 0

            # title tags songs
            my_condition = condition[my_title_len][my_tags_len][my_songs_len]

            if my_condition == self.Condition.SONG_ONLY:
                rec_song_list, rec_tag_list = \
                    solve_song_only(song_sets, tag_sets, title_lists, song_meta, my_songs, my_tags, my_title)
            elif my_condition == self.Condition.TAG_SONG:
                rec_song_list, rec_tag_list = solve_song_tag(song_sets, tag_sets, title_lists,
                                                             song_meta, my_songs, my_tags, my_title)
            elif my_condition == self.Condition.TITLE_TAG:
                rec_song_list, rec_tag_list = solve_title_tag(song_sets, tag_sets, title_lists,
                                                              song_meta, my_songs, my_tags, my_title)
            elif my_condition == self.Condition.TITLE_ONLY:
                rec_song_list, rec_tag_list = solve_title_only(song_sets, tag_sets, title_lists,
                                                               song_meta, my_songs, my_tags, my_title)
            elif my_condition == self.Condition.TAG_ONLY:
                rec_song_list, rec_tag_list = solve_tag_only(song_sets, tag_sets, title_lists,
                                                             song_meta, my_songs, my_tags, my_title)
            elif my_condition == self.Condition.TITLE_SONG:
                rec_song_list, rec_tag_list = solve_title_song(song_sets, tag_sets, title_lists,
                                                               song_meta, my_songs, my_tags, my_title)
            elif my_condition == self.Condition.ALL:
                rec_song_list, rec_tag_list = solve_all(song_sets, tag_sets, title_lists,
                                                        song_meta, my_songs, my_tags, my_title)
            #nothing
            else:
                rec_song_list, rec_tag_list = solve_others(song_sets, tag_sets, title_lists,
                                                           song_meta, my_songs, my_tags, my_title)

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
        write_json(answers, "res/results.json")


if __name__ == "__main__":
    fire.Fire(GenreMostPopular)
