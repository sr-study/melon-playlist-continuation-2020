# -*- coding: utf-8 -*-
from collections import Counter

import fire
import json
import pandas as pd
import os
import distutils.dir_util
import numpy as np
import io

from arena_util import load_json

NUM_CORE = 1


def write_json(data, fname):
    def _conv(o):
        if isinstance(o, np.int64):
            return int(o)
        else:
            return int(o)
        #return o
        #raise TypeError

    parent = os.path.dirname(fname)
    distutils.dir_util.mkpath(parent)
    with io.open(fname, "w", encoding="utf8") as f:
        json_str = json.dumps(data, ensure_ascii=True, default=_conv)
        f.write(json_str)


class MultiprocessSolver:
    def _song_mp_per_genre(self, song_meta, global_mp):
        res = {}

        for sid, song in song_meta.items():
            for genre in song['song_gn_gnr_basket']:
                res.setdefault(genre, []).append(sid)

        for genre, sids in res.items():
            res[genre] = Counter({k: global_mp.get(int(k), 0) for k in sids})
            res[genre] = [k for k, v in res[genre].most_common(200)]

        return res

    def chunker_list(self, seq, size):
        return (seq[i::size] for i in range(size))

    def run(self, song_meta_fname, train_fname, question_fname, jobs=1, train_ans_fname=None):
        global NUM_CORE
        NUM_CORE = jobs

        print("Loading song meta...")
        song_meta_json = load_json(song_meta_fname)

        print("Loading train file...")
        train_data = load_json(train_fname)
        print(len(train_data))

        print("Loading question file...")
        questions = load_json(question_fname)

        print("Loading question file...")
        ans = None
        if train_ans_fname != None:
            ans = load_json(train_ans_fname)

        result_df = pd.DataFrame(
            columns=['id', 'means_music_score', 'mean_tag_score', 'mean_title_score'])

        print("Writing answers...")

        chunked_train_set = list(self.chunker_list(questions, NUM_CORE))
        print(f'run with {len(chunked_train_set)} multiprocess')
        from nns_ensemble_with_artist_dist import GenreMostPopular
        import multiprocessing
        algorithm = GenreMostPopular()

        return_dict = multiprocessing.Manager().dict()
        answers_list = list()
        jobs = []
        p_idxs = []

        for p_idx, train_chunk in enumerate(chunked_train_set):
            p = multiprocessing.Process(target=algorithm._generate_answers,
                                        args=(song_meta_json, train_data, train_chunk, result_df, ans, p_idx, return_dict))
            jobs.append(p)
            p.start()
            p_idxs.append(p_idx)

        for p in jobs:
            p.join()

        answers = list()

        for p_idx in p_idxs:
            answers = answers + return_dict[p_idx]
        write_json(answers, "./cf/results/results.json")


if __name__ == "__main__":
    fire.Fire(MultiprocessSolver)
