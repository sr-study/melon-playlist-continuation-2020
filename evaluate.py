# -*- coding: utf-8 -*-
import fire
import numpy as np

from arena_util import load_json


class ArenaEvaluator:
    def _idcg(self, l):
        return sum((1.0 / np.log(i + 2) for i in range(l)))

    def __init__(self):
        self._idcgs = [self._idcg(i) for i in range(101)]

    def _ndcg(self, gt, rec):
        dcg = 0.0
        for i, r in enumerate(rec):
            if r in gt:
                dcg += 1.0 / np.log(i + 2)

        return dcg / self._idcgs[len(gt)]

    def _eval(self, gt_fname, rec_fname, rec_full_fname):
        gt_playlists = load_json(gt_fname)
        gt_dict = {g["id"]: g for g in gt_playlists}
        rec_playlists = load_json(rec_fname)

        rec_question = load_json(rec_full_fname)
        q_dict = {g["id"]: g for g in rec_question}

        gt_ids = set([g["id"] for g in gt_playlists])
        rec_ids = set([r["id"] for r in rec_playlists])


        if gt_ids != rec_ids:
            raise Exception("결과의 플레이리스트 수가 올바르지 않습니다.")

        rec_song_counts = [len(p["songs"]) for p in rec_playlists]
        rec_tag_counts = [len(p["tags"]) for p in rec_playlists]

        if set(rec_song_counts) != set([100]):
            raise Exception("추천 곡 결과의 개수가 맞지 않습니다.")

        if set(rec_tag_counts) != set([10]):
            raise Exception("추천 태그 결과의 개수가 맞지 않습니다.")

        rec_unique_song_counts = [len(set(p["songs"])) for p in rec_playlists]
        rec_unique_tag_counts = [len(set(p["tags"])) for p in rec_playlists]

        if set(rec_unique_song_counts) != set([100]):
            raise Exception("한 플레이리스트에 중복된 곡 추천은 허용되지 않습니다.")

        if set(rec_unique_tag_counts) != set([10]):
            raise Exception("한 플레이리스트에 중복된 태그 추천은 허용되지 않습니다.")

        music_ndcg = 0.0
        tag_ndcg = 0.0

        case_music = [0.0, 0.0, 0.0, 0.0]
        case_tag = [0.0, 0.0, 0.0, 0.0]
        case_count =[0, 0, 0, 0]

        def check_case (id):
            tag_len =len(q_dict[id]['tags'])
            song_len = len(q_dict[id]['songs'])

            if song_len !=0 and tag_len!=0:
                return 0

            elif song_len ==0 and tag_len!=0:
                return 1

            elif song_len !=0 and tag_len==0:
                return 2
            elif song_len ==0 and tag_len==0:
                return 3


        for rec in rec_playlists:
            gt = gt_dict[rec["id"]]
            cur_music_ndcg = self._ndcg(gt["songs"], rec["songs"][:100])
            cur_tag_ndcg = self._ndcg(gt["tags"], rec["tags"][:10])
            music_ndcg += cur_music_ndcg
            tag_ndcg += cur_tag_ndcg

            case_id =check_case(rec['id'])
            case_music[case_id] += cur_music_ndcg
            case_tag[case_id] += cur_tag_ndcg
            case_count[case_id] += 1


        for idx in range(4):
            case_music[idx]=case_music[idx]/case_count[idx]
            case_tag[idx] =case_tag[idx]/case_count[idx]

        music_ndcg = music_ndcg / len(rec_playlists)
        tag_ndcg = tag_ndcg / len(rec_playlists)
        score = music_ndcg * 0.85 + tag_ndcg * 0.15

        return music_ndcg, tag_ndcg, score ,case_music, case_tag

    def evaluate(self):
        try:
            gt_fname = 'arena_data/answers/val.json'
            rec_fname = 'arena_data/res/results.json'
            rec_full_fname= 'arena_data/questions/val.json'
            music_ndcg, tag_ndcg, score, case_music, case_tag = self._eval(gt_fname, rec_fname, rec_full_fname)
            print('Total score')
            print(f"Music nDCG: {music_ndcg:.6}")
            print(f"Tag nDCG: {tag_ndcg:.6}")
            print(f"Score: {score:.6}")

            case_titles =['song + tag','tag','song','x (title only)']
            for idx , case_title in enumerate(case_titles):
                print(f'#### {case_title}')
                print(f"Music nDCG: {case_music[idx]:.6}")
                print(f"Tag nDCG: {case_tag[idx]:.6}")







        except Exception as e:
            print(e)


if __name__ == "__main__":
    fire.Fire(ArenaEvaluator)
