class NodeManager:
    def __init__(self, nodes=None):
        self._nodes = {}
        if nodes:
            self.add_all(nodes)

    def has(self, node_class, node_id):
        return (node_class, node_id) in self._nodes

    def get(self, node_class, node_id):
        return self._nodes[node_class, node_id]

    def add(self, node):
        if not self.has(node.__class__, node.id):
            self._nodes[node.__class__, node.id] = node

    def add_all(self, nodes):
        for node in nodes:
            self.add(node)

    def to_list(self):
        return list(self._nodes.values())
