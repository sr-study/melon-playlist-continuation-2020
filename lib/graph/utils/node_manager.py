class NodeManager:
    def __init__(self, graph, node_class, validation_checker_func=None):
        self._graph = graph
        self._node_class = node_class
        self._nodes = {}
        self._validation_checker_func = validation_checker_func

    def get_or_create(self, id, **kwargs):
        if self.has(id):
            node = self.get(id)
            if not self._validate(node, id, **kwargs):
                print(f"[Warning] NodeManager<{self._node_class}>.get_or_create(): "
                      "Getting data and creating data is not same.")
            return node
        else:
            return self._create(id, **kwargs)

    def has(self, id):
        return id in self._nodes

    def get(self, id):
        if not self.has(id):
            raise Exception("Node not exists")

        return self._nodes[id]

    def _create(self, id, **kwargs):
        if self.has(id):
            raise Exception("Node already exists")
            
        node = self._graph.add_node(self._node_class, id=id, **kwargs)
        self._nodes[id] = node
        return node

    def _validate(self, node, id, **kwargs):
        if self._validation_checker_func is not None:
            return self._validation_checker_func(node, id, **kwargs)
        else:
            return True
