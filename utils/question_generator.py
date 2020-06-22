import copy
import enum
import numpy as np
from random import Random
from collections import namedtuple
from collections import OrderedDict
from constants import NUM_OF_RECOMMENDED_SONGS as MAX_SONGS
from constants import NUM_OF_RECOMMENDED_TAGS as MAX_TAGS


class QuestionType(enum.Enum):
    ALL = enum.auto()
    SONG_TAG = enum.auto()
    SONG_TITLE = enum.auto()
    TAG_TITLE = enum.auto()
    SONG_ONLY = enum.auto()
    TAG_ONLY = enum.auto()
    TITLE_ONLY = enum.auto()
    NOTHING = enum.auto()


class QuestionGenerator:
    defaultRatio = {
        QuestionType.ALL: 1,
        QuestionType.SONG_TAG: 1,
        QuestionType.SONG_TITLE: 1,
        QuestionType.TAG_TITLE: 1,
        QuestionType.SONG_ONLY: 1,
        QuestionType.TAG_ONLY: 1,
        QuestionType.TITLE_ONLY: 1,
        QuestionType.NOTHING: 1,
    }

    def __init__(self, seed=None, ratio=None):
        self.set_seed(seed)
        self.set_ratio(ratio)

    def set_seed(self, seed):
        self._random = Random(seed)
        return self

    def set_ratio(self, ratio=None):
        if ratio is None:
            ratio = QuestionGenerator.defaultRatio

        self._ratio = ratio
        return self

    def generate(self, playlists):
        original_ids = [p['id'] for p in playlists]
        playlists = self._shuffle(playlists)

        ratio = self._get_normalized_ratio()
        questions, answers = self._generate_questions(playlists, ratio)

        questions = self._sort_playlists(questions, original_ids)
        answers = self._sort_playlists(answers, original_ids)

        return questions, answers

    def _shuffle(self, list_):
        list_ = copy.deepcopy(list_)
        self._random.shuffle(list_)
        return list_

    def _get_normalized_ratio(self):
        normalized_ratio = {}
        total = sum(self._ratio.values())
        for q_type in QuestionType:
            if q_type in self._ratio:
                normalized_ratio[q_type] = self._ratio[q_type] / total
            else:
                normalized_ratio[q_type] = 0

        return normalized_ratio

    def _generate_questions(self, playlists, type_ratio):
        questions = []
        answers = []

        typed_playlists = self._split_playlists_smart(playlists, type_ratio)
        for q_type, q_playlists in typed_playlists.items():
            for playlist in q_playlists:
                question, answer = self._generate_question(playlist, q_type)
                questions.append(question)
                answers.append(answer)

        return questions, answers

    def _generate_question(self, playlist, question_type):
        question_flags = {
            # question_type: (songs, tags, title)
            QuestionType.ALL: (True, True, True),
            QuestionType.SONG_TAG: (True, True, False),
            QuestionType.SONG_TITLE: (True, False, True),
            QuestionType.TAG_TITLE: (False, True, True),
            QuestionType.SONG_ONLY: (True, False, False),
            QuestionType.TAG_ONLY: (False, True, False),
            QuestionType.TITLE_ONLY: (False, False, True),
            QuestionType.NOTHING: (False, False, False),
        }

        question = playlist.copy()
        answer = playlist.copy()
        songs = playlist['songs']
        tags = playlist['tags']
        has_songs, has_tags, has_title = question_flags[question_type]

        if has_songs:
            question['songs'], answer['songs'] = self._mask_list(songs)
        else:
            question['songs'] = []
            answer['songs'] = songs[:MAX_SONGS]

        if has_tags:
            question['tags'], answer['tags'] = self._mask_list(tags)
        else:
            question['tags'] = []
            answer['tags'] = tags[:MAX_TAGS]

        if not has_title:
            question['plylst_title'] = ""

        return question, answer

    def _mask_list(self, list_):
        mask_len = len(list_)
        mask = np.full(mask_len, False)
        mask[mask_len//2:] = True
        np.random.shuffle(mask)

        questions = list(np.array(list_)[np.invert(mask)])
        answers = list(np.array(list_)[mask])
        return questions, answers

    def _split_playlists(self, playlists, type_ratio):
        splitted_playlists = {}

        total = len(playlists)
        acc = 0
        for q_type, q_ratio in type_ratio.items():
            next_acc = acc + q_ratio
            begin = int(acc * total)
            end = int(next_acc * total)
            splitted_playlists[q_type] = playlists[begin:end]
            acc = next_acc

        return splitted_playlists

    def _split_playlists_smart(self, playlists, type_ratio):
        SortMethod = namedtuple('SortMethod', 'key reverse')
        sort_methods = OrderedDict([
            (QuestionType.SONG_TAG, SortMethod(
                key=lambda p: (len(p['songs'])/10) * len(p['tags']),
                reverse=True,
            )),
            (QuestionType.TITLE_ONLY, SortMethod(
                key=lambda p: (len(p['songs'])/10) + len(p['tags']),
                reverse=False,
            )),
            (QuestionType.TAG_TITLE, SortMethod(
                key=lambda p: len(p['songs']),
                reverse=False,
            )),
            (QuestionType.SONG_ONLY, SortMethod(
                key=lambda p: (len(p['songs'])/10) - len(p['tags']),
                reverse=True,
            )),
            (QuestionType.NOTHING, SortMethod(
                key=lambda p: (len(p['songs'])/10) + len(p['tags']),
                reverse=False,
            )),
            (QuestionType.TAG_ONLY, SortMethod(
                key=lambda p: len(p['tags']) - (len(p['songs'])/10),
                reverse=True,
            )),
            (QuestionType.SONG_TITLE, SortMethod(
                key=lambda p: len(p['tags']),
                reverse=False,
            )),
            (QuestionType.ALL, SortMethod(
                key=lambda p: (len(p['songs'])/10) * len(p['tags']),
                reverse=True,
            )),
        ])

        playlists = playlists.copy()
        splitted_playlists = {}

        used = set()
        total = len(playlists)
        acc = 0
        for q_type, method in sort_methods.items():
            q_ratio = type_ratio[q_type]

            next_acc = acc + q_ratio
            begin = int(acc * total)
            end = int(next_acc * total)

            q_list = []
            q_len = end - begin
            playlists = sorted(playlists, key=method.key,
                               reverse=method.reverse)
            n = 0
            for p in playlists:
                if p['id'] in used:
                    continue
                if n >= q_len:
                    break
                q_list.append(p)
                used.add(p['id'])
                n += 1

            splitted_playlists[q_type] = q_list
            acc = next_acc

        return splitted_playlists

    def _sort_playlists(self, playlists, ids):
        playlist_map = {p['id']: p for p in playlists}
        return [playlist_map[id] for id in ids]


def count_questions_by_type(questions):
    type_map = {
        # (songs, tags, title): question_type
        (True, True, True): QuestionType.ALL,
        (True, True, False): QuestionType.SONG_TAG,
        (True, False, True): QuestionType.SONG_TITLE,
        (False, True, True): QuestionType.TAG_TITLE,
        (True, False, False): QuestionType.SONG_ONLY,
        (False, True, False): QuestionType.TAG_ONLY,
        (False, False, True): QuestionType.TITLE_ONLY,
        (False, False, False): QuestionType.NOTHING,
    }

    counts = {t: 0 for t in QuestionType}

    for question in questions:
        songs = question['songs']
        tags = question['tags']
        title = question['plylst_title']

        has_songs = len(songs) > 0
        has_tags = len(tags) > 0
        has_title = title != ""

        question_type = type_map[has_songs, has_tags, has_title]
        counts[question_type] += 1

    return counts
