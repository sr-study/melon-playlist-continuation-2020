# -*- coding: utf-8 -*-
import fire
from tqdm import tqdm

import lib.graph
import lib.grape
from constants import NUM_OF_RECOMMENDED_SONGS
from constants import NUM_OF_RECOMMENDED_TAGS
from utils import read_json
from utils import write_json
from utils import validate_answers


class GrapeRecommender:
    def run(self, song_meta_fname, genre_fname, train_fname, question_fname):
        print("Loading song meta...")
        song_meta = read_json(song_meta_fname)

        print("Loading genre...")
        genre_data = read_json(genre_fname)

        print("Loading train file...")
        train_data = read_json(train_fname)

        print("Building graph...")
        graph = lib.graph.GraphBuilder() \
            .build(song_meta, genre_data, train_data)

        print("Fitting train data...")
        grape = lib.grape.Grape(
            graph,
            NUM_OF_RECOMMENDED_SONGS,
            NUM_OF_RECOMMENDED_TAGS,
        ).fit(train_data)

        print("Loading question file...")
        questions = read_json(question_fname)

        print("Writing answers...")
        answers = grape.predict_all(questions)
        write_json(answers, "./arena_data/results/results.json")
        validate_answers(answers, questions)


if __name__ == "__main__":
    fire.Fire(GrapeRecommender)
