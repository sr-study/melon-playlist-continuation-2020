# -*- coding: utf-8 -*-
import io
import os
import json
import distutils.dir_util
from collections import Counter
import numpy as np

import numpy as np
import pandas as pd

def write_json(data, fname):
    def _conv(o):
        if isinstance(o, np.int64):
            return int(o)
        else:
            return int(o)
        #return o
        #raise TypeError

    parent = os.path.dirname(fname)
    distutils.dir_util.mkpath("./arena_data/" + parent)
    with io.open("./arena_data/" + fname, "w", encoding="utf8") as f:
        json_str = json.dumps(data, ensure_ascii=True, default=_conv)
        f.write(json_str)


def load_json(fname):
    with open(fname, encoding="UTF-8") as f:
        json_obj = json.load(f)

    return json_obj

def load_json_to_df(fname):
    df = pd.read_json(fname,encoding="UTF-8")
    return df


def debug_json(r):
    print(json.dumps(r, ensure_ascii=False, indent=4))


def remove_seen(seen, l):
    seen = set(seen)
    return [x for x in l if not (x in seen)]


def most_popular(playlists, col, topk_count):
    c = Counter()

    for doc in playlists:
        c.update(doc[col])

    topk = c.most_common(topk_count)
    return c, [k for k, v in topk]
