import collections


class ScoreMap(collections.defaultdict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, other_dict, modify=False):
        if not modify:
            return self.copy().add(other_dict, modify=True)

        for k, v in other_dict.items():
            self[k] += v

        return self

    def increase(self, keys, increment, modify=False):
        if not modify:
            return self.copy().increase(keys, increment, modify=True)

        for k in keys:
            self[k] += increment

        return self

    def filter(self, func):
        return ScoreMap(self.default_factory, {k: v for k, v in self.items() if func(k, v)})

    def top(self, n=None):
        sorted_list = sorted(self.items(), key=lambda t: t[1], reverse=True)
        if n is None:
            return sorted_list
        else:
            return sorted_list[:n]

    def top_keys(self, n=None):
        sorted_list = sorted(self, key=self.get, reverse=True)
        if n is None:
            return sorted_list
        else:
            return sorted_list[:n]
