import json
from .node import Node
from .edge import Edge


class Graph:
    def __init__(self, data_path="data/graph.json", autosave=True):
        self.nodes = []
        self.edges = []
        self.data_path = data_path
        self.autosave = autosave

    # =========================
    # INTERNAL AUTOSAVE
    # =========================
    def _autosave(self):
        if self.autosave and self.data_path:
            self.save_to_json(self.data_path)

    # =========================
    # JSON İŞLEMLERİ
    # =========================
    def load_from_json(self, path):
        with open(path, "r") as f:
            data = json.load(f)

        self.nodes = [
            Node(
                n["id"],
                n["name"],
                n["aktiflik"],
                n["etkilesim"],
                n["baglanti_sayisi"],
                n["komsular"]
            )
            for n in data["nodes"]
        ]

        self.edges = [
            Edge(e["from"], e["to"], e["weight"]) for e in data["edges"]
        ]

    def save_to_json(self, path):
        data = {
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "aktiflik": n.aktiflik,
                    "etkilesim": n.etkilesim,
                    "baglanti_sayisi": n.baglanti_sayisi,
                    "komsular": n.komsular
                }
                for n in self.nodes
            ],
            "edges": [
                {
                    "from": e.source,
                    "to": e.target,
                    "weight": e.weight
                }
                for e in self.edges
            ]
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    # =========================
    # NODE İŞLEMLERİ
    # =========================
    def get_node_by_id(self, node_id):
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def add_node(self, node: Node):
        if self.get_node_by_id(node.id) is not None:
            raise ValueError(f"Aynı ID'ye sahip node zaten var: {node.id}")

        self.nodes.append(node)
        self._autosave()

    def remove_node(self, node_id):
        node = self.get_node_by_id(node_id)
        if node is None:
            raise ValueError("Node bulunamadı")

        self.nodes = [n for n in self.nodes if n.id != node_id]

        self.edges = [
            e for e in self.edges
            if e.source != node_id and e.target != node_id
        ]

        for n in self.nodes:
            if node_id in n.komsular:
                n.komsular.remove(node_id)

        self._autosave()

    # =========================
    # AĞIRLIK HESAPLAMA
    # =========================
    def calculate_weight(self, node1: Node, node2: Node):
        return 1 / (
            1
            + (node1.aktiflik - node2.aktiflik) ** 2
            + (node1.etkilesim - node2.etkilesim) ** 2
            + (node1.baglanti_sayisi - node2.baglanti_sayisi) ** 2
        )

    # =========================
    # EDGE İŞLEMLERİ
    # =========================
    def edge_exists(self, source_id, target_id):
        for e in self.edges:
            if (e.source == source_id and e.target == target_id) or \
               (e.source == target_id and e.target == source_id):
                return True
        return False

    def add_edge(self, source_id, target_id):
        if source_id == target_id:
            raise ValueError("Self-loop yasak")

        node1 = self.get_node_by_id(source_id)
        node2 = self.get_node_by_id(target_id)

        if node1 is None or node2 is None:
            raise ValueError("Node bulunamadı")

        if self.edge_exists(source_id, target_id):
            raise ValueError("Bu edge zaten var")

        weight = self.calculate_weight(node1, node2)

        self.edges.append(Edge(source_id, target_id, weight))

        node1.komsular.append(target_id)
        node2.komsular.append(source_id)

        node1.baglanti_sayisi += 1
        node2.baglanti_sayisi += 1

        self._autosave()
