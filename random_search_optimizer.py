import copy
import numpy as np
from collections import OrderedDict


class RandomSearchOptimizer:
    def __init__(self, func, params, seed=None):
        self._func = func
        self._params = OrderedDict(params)
        self._seed = seed
        self._rand = np.random.RandomState(seed)
        self._records = []
        self._col_width = 10

    def run(self, n_iters):
        self._print_head()

        for i in range(n_iters):
            index = len(self._records)
            params = self._next_params()
            targets = self._func(**params)
            record = {
                'targets': targets,
                'params': params,
            }
            self._records.append(record)

            self._print_record(index, record)

    def get_maximum_params(self):
        record = max(self._records, key=lambda r: r['targets'])
        return copy.deepcopy(record['params'])

    def get_params_by_index(self, index):
        rand = np.random.RandomState(self._seed)
        for _ in range(index):
            self._next_params(rand)
        return self._next_params(rand)

    def print_records(self):
        self._print_head()
        for i, record in enumerate(self._records):
            self._print_record(i, record)

    def _next_params(self, rand=None):
        if rand is None:
            rand = self._rand

        ranges = dict(self._params)
        for k, v in ranges.items():
            if type(v) != tuple:
                ranges[k] = (v, v)
        ranges = sorted(list(ranges.items()))

        generated_params = OrderedDict(self._params)
        for k, r in ranges:
            generated_params[k] = rand.uniform(r[0], r[1], size=1)[0]

        return generated_params

    def _print_head(self):
        w = self._col_width
        def col_name(s):
            return f"{_ellipsis(s, w):{w}}"

        head = "|"
        head += f"{col_name('index')}|"
        head += f"{col_name('al_songs')}|"
        head += f"{col_name('al_tags')}|"
        head += f"{col_name('al_score')}|"
        head += f"{col_name('st_songs')}|"
        head += f"{col_name('st_tags')}|"
        head += f"{col_name('st_score')}|"
        head += f"{col_name('tt_songs')}|"
        head += f"{col_name('tt_tags')}|"
        head += f"{col_name('tt_score')}|"
        head += f"{col_name('so_songs')}|"
        head += f"{col_name('so_tags')}|"
        head += f"{col_name('so_score')}|"
        head += f"{col_name('to_songs')}|"
        head += f"{col_name('to_tags')}|"
        head += f"{col_name('to_score')}|"
        for k in self._params:
            head += f"{col_name(k)}|"
        print(head)

        line = "="
        line += "=" * (w + 1)
        line += "=" * (w + 1)
        for k in self._params:
            line += "=" * (w + 1)
        print(line)

    def _print_record(self, index, record):
        w = self._col_width

        targets = record['targets']
        params = record['params']

        body = "|"
        body += f"{index:>{w}}|"
        body += f"{targets['al_songs']:>{w}}|"
        body += f"{targets['al_tags']:>{w}}|"
        body += f"{targets['al_score']:>{w}}|"
        body += f"{targets['st_songs']:>{w}}|"
        body += f"{targets['st_tags']:>{w}}|"
        body += f"{targets['st_score']:>{w}}|"
        body += f"{targets['tt_songs']:>{w}}|"
        body += f"{targets['tt_tags']:>{w}}|"
        body += f"{targets['tt_score']:>{w}}|"
        body += f"{targets['so_songs']:>{w}}|"
        body += f"{targets['so_tags']:>{w}}|"
        body += f"{targets['so_score']:>{w}}|"
        body += f"{targets['to_songs']:>{w}}|"
        body += f"{targets['to_tags']:>{w}}|"
        body += f"{targets['to_score']:>{w}}|"
        for k in self._params:
            body += f"{params[k]:>{w}.4f}|"
        print(body, flush=True)


def _ellipsis(s, max_length):
    if len(s) > max_length:
        return s[:max_length - 2] + ".."
    return s
