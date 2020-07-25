from ..collections import OrderedSet


def remove_seen(l, seen, max_length=-1):
    if max_length < 0:
        max_length = len(l)

    results = []
    seen = set(seen)
    for x in l:
        if x in seen:
            continue
        if len(results) >= max_length:
            break

        results.append(x)

    return results


def merge_uniques(*lists):
    uniques = OrderedSet()
    for list_ in lists:
        uniques |= list_

    return list(uniques)
