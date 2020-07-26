import json
from enum import Enum, auto
from collections import Counter



def read_json(file_path):
    with open(file_path, encoding='UTF8') as json_file:
        json_data = json.load(json_file)
        return json_data

def write_json(data, file_path):
    with open(file_path, 'w') as cur_json:
        json.dump(data, cur_json)


class ProblemType(Enum):
    SONG_ONLY = auto()
    SONG_TAG = auto()
    TAG_TITLE = auto()
    TITLE_ONLY = auto()
    ELSE = auto()


class Ensembler():
    def __init__(self, file_paths, question_path):
        self.results = list()

        self.tot_intersect_song = 0
        self.tot_intersect_tag = 0

        for file_path in file_paths:
            self.results.append(read_json(file_path))
        self.q = read_json(question_path)
        print(type(self.q))
        self.q_dict = {g['id']: {'songs': g['songs'], 'tags': g['tags'], 'title': g['plylst_title']} for g in self.q}
        print(self.q_dict)

    def get_problem_type(self, id):
        question = self.q_dict[id]
        # song
        if len(question['songs']) != 0 and len(question['tags']) == 0 and len(question['title']) == 0:
            return ProblemType.SONG_ONLY
        # song tag
        if len(question['songs']) != 0 and len(question['tags']) != 0 and len(question['title']) == 0:
            return ProblemType.SONG_TAG
        # tag title
        if len(question['songs']) == 0 and len(question['tags']) != 0 and len(question['title']) != 0:
            return ProblemType.TAG_TITLE
        # title
        if len(question['songs']) == 0 and len(question['tags']) == 0 and len(question['title']) != 0:
            return ProblemType.TITLE_ONLY
        return ProblemType.ELSE

    def score_ensemble_lists(self, lists, rec_sz, name=None):
        score_dict = {}
        def score_function(idx):
            # linear_model
            return 100 - idx
        for each_list in lists:
            for idx,val in enumerate(each_list):
                if val in score_dict.keys():
                    score_dict[val] += score_function(idx)
                else:
                    score_dict[val]  =score_function(idx)

        sorted_socre = sorted(score_dict.items(),key=lambda  x: x[1],reverse=True)
        result = []
        for i in range(rec_sz):
            result.append(sorted_socre[i][0])
        return result

    def get_intersects(self, lists):
        merged_list = list()

        for cur_list in lists:
            for element in cur_list:
                merged_list.append(element)

        intersect_counter = Counter(merged_list)
        intersects = list()

        for key, val in intersect_counter.items():
            if val == len(lists):
                intersects.append(key)

        return intersects

    def ensemble_two_lists(self, lists, rec_sz, name=None):
        unit = len(lists)
        ensembled_list = self.get_intersects(lists)
        if name == 'song':
            self.tot_intersect_song += len(ensembled_list)
        else:
            self.tot_intersect_tag += len(ensembled_list)
        ptr_list = [0] * unit

        cnt = 0
        while len(ensembled_list) < rec_sz:
            ptr = cnt % unit

            cur_list = lists[ptr]
            while (ptr_list[ptr] < len(lists[ptr])) and (cur_list[ptr_list[ptr]] in ensembled_list):
                ptr_list[ptr] += 1

            if ptr_list[ptr] < len(lists[ptr]):
                cur = lists[ptr][ptr_list[ptr]]
                ptr_list[ptr] += 1

                ensembled_list.append(cur)

            cnt += 1
        return ensembled_list

    def ensemble(self):
        res_json = list()
        results = self.results

        for result in results:
            result.sort(key=lambda x: x['id'])

        for cur_res_list in zip(*results):
            song_lists = list()
            tag_lists = list()

            for cur_res in cur_res_list:
                song_list = cur_res['songs']
                tag_list = cur_res['tags']

                song_lists.append(song_list)
                tag_lists.append(tag_list)
                
            # 0이 그래프, 1이 카트
            problem_type = self.get_problem_type(cur_res['id'])
            # ensembled_songs = self.score_ensemble_lists(song_lists, 100, 'song')
            # ensembled_tags = self.score_ensemble_lists(tag_lists, 10, 'tag')

            if problem_type == ProblemType.SONG_ONLY:
                ensembled_songs = self.score_ensemble_lists(song_lists, 100, 'song')
                ensembled_tags = tag_lists[1]
            elif problem_type == ProblemType.SONG_TAG:
                ensembled_songs = self.score_ensemble_lists(song_lists, 100, 'song')
                ensembled_tags = tag_lists[1]
            elif problem_type == ProblemType.TAG_TITLE:
                ensembled_songs = self.score_ensemble_lists(song_lists, 100, 'song')
                ensembled_tags = tag_lists[0]
            elif problem_type == ProblemType.TITLE_ONLY:
                ensembled_songs = song_lists[1]
                ensembled_tags = tag_lists[1]
            else:
                ensembled_songs = self.score_ensemble_lists(song_lists, 100, 'song')
                ensembled_tags = self.score_ensemble_lists(tag_lists, 10, 'tag')

            cur_res = {
              'id': cur_res_list[0]['id'],
              'songs': ensembled_songs,
              'tags': ensembled_tags,
            }
            validate_answer(cur_res)
            res_json.append(cur_res)
        print(f'total intersect songs : {self.tot_intersect_song}')
        print(f'total intersect tags : {self.tot_intersect_tag}')
        return res_json

NUM_OF_RECOMMENDED_SONGS = 100
NUM_OF_RECOMMENDED_TAGS = 10


def validate_answer(answer):
    if len(answer['songs']) != NUM_OF_RECOMMENDED_SONGS:
        raise Exception("추천 곡 결과의 개수가 맞지 않습니다.")

    if len(answer['tags']) != NUM_OF_RECOMMENDED_TAGS:
        raise Exception("추천 태그 결과의 개수가 맞지 않습니다.")

    if len(set(answer['songs'])) != NUM_OF_RECOMMENDED_SONGS:
        raise Exception("한 플레이리스트에 중복된 곡 추천은 허용되지 않습니다.")

    if len(set(answer['tags'])) != NUM_OF_RECOMMENDED_TAGS:
        raise Exception("한 플레이리스트에 중복된 태그 추천은 허용되지 않습니다.")

    return True


ensembler = Ensembler(['./grape_semi/results_test.json', './cf_semi/results_test.json'], './res/test.json')
res = ensembler.ensemble()
# print(res)
write_json(res, 'results.json')
