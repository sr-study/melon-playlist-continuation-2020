import fire
import os
import sys
sys.path.append('./graph')
sys.path.append('./cf')

from ensembler import Ensembler
from cf.solve_multiprocess import MultiprocessSolver
from graph.grape_recommender import GrapeRecommender
from arena_util import load_json
from arena_util import write_json


MERGED_TRAIN_FNAME = './arena_data/merged_train.json'
RUNNING_IN_WINDOWS = os.name == 'nt'


class Recommend:
    def run(self, song_meta_fname, train_fname, question_fname, genre_fname, val_fname=None, test_fname=None, jobs=1):
        wanna_use_merged_train = (val_fname is not None) and (test_fname is not None)
        if wanna_use_merged_train:
            # self.merge_trains([train_fname, val_fname, test_fname], MERGED_TRAIN_FNAME)
            self.reproduce_train(train_fname, val_fname, test_fname, MERGED_TRAIN_FNAME)

        graph_train_fname = MERGED_TRAIN_FNAME if wanna_use_merged_train else train_fname
        graph_jobs = 1 if RUNNING_IN_WINDOWS else jobs

        if RUNNING_IN_WINDOWS and jobs > 1:
            print("[Warning] 그래프 추천은 윈도우 환경에서 멀티프로세싱이 불가능 합니다.")

        cf_solver = MultiprocessSolver()
        cf_solver.run(song_meta_fname=song_meta_fname,
                      train_fname=train_fname,
                      question_fname=question_fname,
                      jobs=jobs)

        graph_solver = GrapeRecommender()
        graph_solver.run(song_meta_fname=song_meta_fname,
                         train_fname=graph_train_fname,
                         question_fname=question_fname,
                         genre_fname=genre_fname,
                         jobs=jobs
                         )

        ensembler = Ensembler(['./graph/results/results.json', './cf/results/results.json'], question_fname)
        res = ensembler.ensemble()
        print(res[0])
        write_json(res, './results/results.json')

    def merge_trains(self, train_fnames, output_fname):
        merged_train = []
        for train_fname in train_fnames:
            merged_train += load_json(train_fname)

        write_json(merged_train, output_fname)

    # 제출 재현용 코드
    # 원래는 merge_trains()만 호출하면 더 좋지만, 제출 당시 사용한 인풋을
    # 재현하기 위해 split 하는 코드를 추가...
    def reproduce_train(self, train_fname, val_fname, test_fname, output_fname):
        from graph.split_data import ArenaSplitter

        splitter = ArenaSplitter()
        splitter.run(train_fname, 0.002, suffix='0002')
        train_fname = './arena_data/orig/train0002.json'

        self.merge_trains([train_fname, val_fname, test_fname], output_fname)


if __name__ == "__main__":
    fire.Fire(Recommend)