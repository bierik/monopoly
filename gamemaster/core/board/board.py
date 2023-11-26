import networkx as nx
from networkx.readwrite import json_graph
from pydash import pick


class Board(nx.DiGraph):
    def __init__(self, root_node, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_node = root_node

    def to_json(self):
        node_link_data = pick(json_graph.node_link_data(self), "nodes", "links")
        node_link_data["root_node"] = self.root_node
        return node_link_data

    def successor_of(self, tile, num_successors=1):
        successor = next(self.successors(tile))
        for i in range(num_successors - 1):
            successor = next(self.successors(successor))
        return successor
