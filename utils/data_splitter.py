import copy
from random import Random


class DataSplitter:
    def __init__(self, seed=None, ratio=0.2):
        self.set_seed(seed)
        self.set_ratio(ratio)

    def set_seed(self, seed):
        self._seed = seed
        return self

    def set_ratio(self, ratio):
        self._ratio = ratio
        return self

    def split(self, playlists):
        random = Random(self._seed)

        playlists = copy.deepcopy(playlists)
        random.shuffle(playlists)

        total = len(playlists)
        mid = int(total * self._ratio)
        train = playlists[mid:]
        val = playlists[:mid]

        return train, val
