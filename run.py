import fire
import sys
sys.path.append('./graph')
sys.path.append('./cf')

from ensembler import Ensembler
from cf.solve_multiprocess import MultiprocessSolver
from graph.grape_recommender import GrapeRecommender
from arena_util import write_json


class Recommend:
    def run(self, song_meta_fname, train_fname, question_fname, genre_fname):
        cf_solver = MultiprocessSolver()
        cf_solver.run(song_meta_fname=song_meta_fname,
                      train_fname=train_fname,
                      question_fname=question_fname,
                      jobs=6)

        graph_solver = GrapeRecommender()
        graph_solver.run(song_meta_fname=song_meta_fname,
                         train_fname=train_fname,
                         question_fname=question_fname,
                         genre_fname=genre_fname,
                         jobs=6
                         )

        ensembler = Ensembler(['./graph/results/results.json', './cf/results/results.json'], question_fname)
        res = ensembler.ensemble()
        print(res[0])
        write_json(res, './results/results.json')

if __name__ == "__main__":
    fire.Fire(Recommend)