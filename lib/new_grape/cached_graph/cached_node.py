from collections import defaultdict


class CachedNode:
    __slots__ = ['type', 'id', 'data', 'index', 'related_nodes']

    def __init__(self, node_type, node_id, data, index):
        self.type = node_type
        self.id = node_id
        self.data = data
        self.index = index
        self.related_nodes = defaultdict(list)

        self.data['indegree'] = 0
        self.data['outdegree'] = 0

    def add_related_node(self, dst, relation):
        self.related_nodes[relation].append(dst)
        self.data['outdegree'] += 1
        dst.data['indegree'] += 1

    def state(self):
        return [self.type, self.id, self.data]
