# -*- coding: utf-8 -*-
import itertools
import multiprocessing as mp
import fire
import numpy as np
from tqdm import tqdm

from lib.grape import Grape
from utils import read_json
from utils import write_json
from utils import validate_answers


class GrapeRecommender:
    def __init__(self):
        self.grape = Grape()

    def run(self, song_meta_fname, genre_fname, train_fname, question_fname, output_fname="./graph/results/results.json", jobs=1, verbose=True):
        self.read_and_fit(song_meta_fname, genre_fname, train_fname, verbose=verbose)
        self.read_and_predict(question_fname, output_fname, jobs=jobs, verbose=verbose)

    def read_and_fit(self, song_meta_fname, genre_fname, train_fname, verbose=True):
        _print("Loading song meta...", verbose=verbose)
        song_meta = read_json(song_meta_fname)

        _print("Loading genre...", verbose=verbose)
        genre_data = read_json(genre_fname)

        _print("Loading train file...", verbose=verbose)
        train_data = read_json(train_fname)

        _print("Fitting train data...", verbose=verbose)
        self.fit(song_meta, genre_data, train_data, verbose=verbose)

    def fit(self, song_meta, genre, train, verbose=True):
        self.grape.fit(song_meta, genre, train, verbose=verbose)

    def set_params(self, **params):
        self.grape.set_params(**params)

    def get_params(self):
        return self.grape.params()

    def save_model(self, path):
        self.grape.save(path)

    def load_model(self, path):
        self.grape.load(path)

    def read_and_predict(self, question_fname, output_fname=None, jobs=1, verbose=True):
        _print("Loading question file...", verbose=verbose)
        questions = read_json(question_fname)

        _print("Predicting...", verbose=verbose)
        results = self.predict(questions, jobs=jobs, verbose=verbose)

        if output_fname is not None:
            _print("Writing results...", verbose=verbose)
            write_json(results, output_fname)

        validate_answers(results, questions)

    def predict(self, questions, jobs=1, verbose=True):
        if jobs > 1:
            return self._predict_multi(questions, jobs, verbose)
        else:
            return self._predict_single(questions, verbose)

    def _predict_multi(self, questions, jobs, verbose=True):
        global _recommender
        _recommender = self

        questions_chunks = list(np.array_split(questions, jobs))
        verbose_chunks = [verbose] * jobs
        chunks = zip(questions_chunks, verbose_chunks)

        with mp.Pool() as pool:
            results = pool.starmap(_predict, chunks)

        return list(itertools.chain(*results))

    def _predict_single(self, questions, verbose=True):
        if verbose:
            return [self.grape(question) for question in tqdm(questions)]
        else:
            return [self.grape(question) for question in questions]


def _predict(questions, verbose=True):
    global _recommender
    return _recommender._predict_single(questions, verbose)


def _print(*args, verbose=True, **kwargs):
    if verbose:
        print(*args, **kwargs)


if __name__ == "__main__":
    fire.Fire(GrapeRecommender)
