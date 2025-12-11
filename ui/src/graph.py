import json
from src.node import Node
from src.edge import Edge

class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def load_from_json(self, path):
        with open(path, "r") as f:
            data = json.load(f)

        # Node yükle
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

        # Edge yükle
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
