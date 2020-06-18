from .ordered_set import OrderedSet


def merge_unique_lists(*lists):
    elements = OrderedSet()
    for list_ in lists:
        elements |= list_

    return list(elements)


def convert_to_ids(nodes):
    return [node.id for node in nodes]


def get_most_common_keys(counter, n=None):
    return [k for k, v in counter.most_common(n)]


def remove_seen(l, seen):
    seen = set(seen)
    return [x for x in l if not (x in seen)]
