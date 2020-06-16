import json
import os
import distutils.dir_util
import numpy as np


def read_json(fname):
    with open(fname, encoding='utf-8') as f:
        json_obj = json.load(f)

    return json_obj


def write_json(data, fname):
    def _conv(o):
        if isinstance(o, (np.int64, np.int32)):
            return int(o)
        raise TypeError

    parent = os.path.dirname(fname)
    distutils.dir_util.mkpath(parent)
    with open(fname, 'w', encoding='utf-8') as f:
        json_str = json.dumps(data, ensure_ascii=False, default=_conv)
        f.write(json_str)
