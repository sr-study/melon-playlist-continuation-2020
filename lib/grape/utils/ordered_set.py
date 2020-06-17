import collections


class OrderedSet(collections.MutableSet):
    def __init__(self, iterable=None):
        self._dict = collections.OrderedDict()
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self._dict)

    def __contains__(self, key):
        return key in self._dict

    def add(self, key):
        self._dict[key] = True

    def discard(self, key):
        self._dict.pop(key)

    def __iter__(self):
        for curr in self._dict:
            yield curr

    def __reversed__(self):
        for curr in self._dict[::-1]:
            yield curr

    def pop(self, last=True):
        if not self:
            raise KeyError('pop from an empty set')
        return self._dict.popitem(last)[0]

    def __repr__(self):
        if not self:
            return f'{self.__class__.__name__}()'
        return f'{self.__class__.__name__}({list(self)})'

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return self._dict == other._dict
        return set(self) == set(other)
