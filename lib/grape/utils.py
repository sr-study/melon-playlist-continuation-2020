from collections import OrderedDict


def merge_unique_lists(*lists):
    elements = OrderedDict()
    for list_ in lists:
        elements.update(OrderedDict(((e, True) for e in list_)))

    return list(elements.keys())


def convert_to_ids(nodes):
    return [node.id for node in nodes]
