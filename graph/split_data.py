# -*- coding: utf-8 -*-
import fire

from utils import DataSplitter
from utils import QuestionType
from utils import QuestionGenerator
from utils import count_questions_by_type
from utils import read_json
from utils import write_json


class ArenaSplitter:
    def run(self, fname, ratio=0.2, suffix=''):
        seed = 777

        print("Reading data...\n")
        playlists = read_json(fname)
        print(f"Total playlists: {len(playlists)}")

        print("Splitting data...")
        train, val = DataSplitter() \
            .set_seed(seed) \
            .set_ratio(ratio) \
            .split(playlists)

        write_json(train, f"arena_data/orig/train{suffix}.json")
        write_json(val, f"arena_data/orig/val{suffix}.json")

        print("Generating questions...")
        questions, answers = QuestionGenerator() \
            .set_seed(seed) \
            .set_ratio({
                QuestionType.SONG_ONLY: 0.42,
                QuestionType.SONG_TAG: 0.39,
                QuestionType.TAG_TITLE: 0.12,
                QuestionType.TITLE_ONLY: 0.07,
                QuestionType.SONG_TITLE: 0,
                QuestionType.TAG_ONLY: 0,
                QuestionType.NOTHING: 0,
                QuestionType.ALL: 0,
            }) \
            .generate(val)

        write_json(questions, f"arena_data/questions/val{suffix}.json")
        write_json(answers, f"arena_data/answers/val{suffix}.json")

        counts = count_questions_by_type(questions)
        print(", ".join([f"{t.name}: {n}" for t, n in counts.items()]))


if __name__ == "__main__":
    fire.Fire(ArenaSplitter)
