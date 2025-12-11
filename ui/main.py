from src.graph import Graph

g = Graph()
g.load_from_json("data/graph.json")

print("Graf başarıyla yüklendi. Node sayısı:", len(g.nodes))
