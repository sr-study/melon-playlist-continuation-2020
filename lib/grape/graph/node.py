class Node:
    __slots__ = ['type', 'id', 'data']

    def __init__(self, node_type, node_id, data=None):
        self.type = node_type
        self.id = node_id
        self.data = data

    def state(self):
        return [self.type, self.id, self.data]

    @classmethod
    def from_state(cls, state):
        return Node(*state)
