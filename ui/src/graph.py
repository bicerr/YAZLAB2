import json
import os
from collections import deque

from .node import Node
from .edge import Edge


class Graph:
    def __init__(self, data_path=None, autosave=True):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_path = data_path or os.path.join(base_dir, "data", "graph.json")
        self.autosave = autosave

        self.nodes = []
        self.edges = []

        if os.path.exists(self.data_path):
            self.load_from_json(self.data_path)

    # =========================
    # CSV İŞLEMLERİ (YENİ)
    # =========================
    def load_from_csv(self, path):
        import csv
        import random
        self.nodes = []
        self.edges = []
        
        # Helper to get or create node
        def get_or_create(nid):
            n = self.get_node_by_id(nid)
            if not n:
                # Randomize attributes
                act = round(random.uniform(0.1, 1.0), 2)
                inter = random.randint(1, 100)
                n = Node(nid, f"Node {nid}", act, inter) 
                self.nodes.append(n)
            return n

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2: continue
                # Expected: Source, Target, [Weight]
                try:
                    s_id = int(row[0])
                    t_id = int(row[1])
                    w = float(row[2]) if len(row) > 2 else 1.0
                    
                    n1 = get_or_create(s_id)
                    n2 = get_or_create(t_id)
                    
                    if not self.edge_exists(s_id, t_id):
                        self.edges.append(Edge(s_id, t_id, w))
                        
                        # Update neighbors
                        if t_id not in n1.komsular: n1.komsular.append(t_id)
                        if s_id not in n2.komsular: n2.komsular.append(s_id)
                        n1.baglanti_sayisi = len(n1.komsular)
                        n2.baglanti_sayisi = len(n2.komsular)
                except ValueError:
                    continue # Skip header or invalid rows

        self._autosave()

    # =========================
    # JSON İŞLEMLERİ
    # =========================
    def load_from_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
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
            for n in data.get("nodes", [])
        ]

        self.edges = [
            Edge(e["from"], e["to"], e["weight"])
            for e in data.get("edges", [])
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

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _autosave(self):
        if self.autosave and self.data_path:
            self.save_to_json(self.data_path)

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

    def update_node(self, node_id, name=None, aktiflik=None, etkilesim=None):
        node = self.get_node_by_id(node_id)
        if node is None:
            raise ValueError("Node bulunamadı")

        if name is not None:
            node.name = name
        if aktiflik is not None:
            node.aktiflik = float(aktiflik)
        if etkilesim is not None:
            node.etkilesim = int(etkilesim)

 
        node.baglanti_sayisi = len(node.komsular)

        for e in self.edges:
            if e.source == node_id or e.target == node_id:
                n1 = self.get_node_by_id(e.source)
                n2 = self.get_node_by_id(e.target)
                e.weight = self.calculate_weight(n1, n2)

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

        # komşuluk tekrarını engelle
        if target_id not in node1.komsular:
            node1.komsular.append(target_id)
        if source_id not in node2.komsular:
            node2.komsular.append(source_id)

        node1.baglanti_sayisi = len(node1.komsular)
        node2.baglanti_sayisi = len(node2.komsular)

        self._autosave()
        
    def remove_edge(self, source_id, target_id):
    # Edge var mı?
        removed = False
        new_edges = []

        for e in self.edges:
            if (e.source == source_id and e.target == target_id) or (e.source == target_id and e.target == source_id):
                removed = True
            else:
                new_edges.append(e)

        if not removed:
            raise ValueError("Edge bulunamadı")

        self.edges = new_edges

    # Komşulukları güncelle
        n1 = self.get_node_by_id(source_id)
        n2 = self.get_node_by_id(target_id)

        if n1 and target_id in n1.komsular:
            n1.komsular.remove(target_id)
            n1.baglanti_sayisi = len(n1.komsular)

        if n2 and source_id in n2.komsular:
            n2.komsular.remove(source_id)
            n2.baglanti_sayisi = len(n2.komsular)

        self._autosave()



        

    # =========================
    # BFS (Breadth First Search)
    # =========================
    def bfs(self, start_node_id):
        start_node = self.get_node_by_id(start_node_id)
        if start_node is None:
            raise ValueError("Başlangıç node'u bulunamadı")

        visited = set()
        queue = deque()
        result = []

        queue.append(start_node_id)
        visited.add(start_node_id)

        while queue:
            current_id = queue.popleft()
            result.append(current_id)

            current_node = self.get_node_by_id(current_id)
            for komsu_id in current_node.komsular:
                if komsu_id not in visited:
                    visited.add(komsu_id)
                    queue.append(komsu_id)

        print("BFS sonucu:", result)
        return result

    # =========================
    # DFS (Depth First Search)
    # =========================
    def dfs(self, start_node_id):
        start_node = self.get_node_by_id(start_node_id)
        if start_node is None:
            raise ValueError("Başlangıç node'u bulunamadı")

        visited = set()
        result = []

        def _dfs(current_id):
            visited.add(current_id)
            result.append(current_id)

            current_node = self.get_node_by_id(current_id)
            for komsu_id in current_node.komsular:
                if komsu_id not in visited:
                    _dfs(komsu_id)

        _dfs(start_node_id)

        print("DFS sonucu:", result)
        return result
    
        # =========================
    # Connected Components
    # =========================
    def connected_components(self):
        visited = set()
        components = []

    # Tüm node’ları dolaş (izole node dahil)
        for node in self.nodes:
            if node.id in visited:
                continue

        # Yeni bileşen başlat
            comp = []
            stack = [node.id]
            visited.add(node.id)

            while stack:
                current_id = stack.pop()
                comp.append(current_id)

                current_node = self.get_node_by_id(current_id)
                if current_node is None:
                    continue

                for nb in current_node.komsular:
                    if nb not in visited:
                        visited.add(nb)
                        stack.append(nb)

            components.append(comp)

        return components


                # =========================
    # Degree Centrality (Top 5)
    # =========================
    def degree_centrality_top5(self):
        # (node_id, degree) listesi
        degrees = [(n.id, len(n.komsular)) for n in self.nodes]

        # degree büyükten küçüğe sırala
        degrees.sort(key=lambda x: x[1], reverse=True)

        # ilk 5
        return degrees[:5]

    # =========================
    # Dijkstra En Kısa Yol
    # =========================
    def dijkstra(self, start_id, end_id):
        if self.get_node_by_id(start_id) is None or self.get_node_by_id(end_id) is None:
            raise ValueError("Başlangıç veya hedef node bulunamadı")

        # Mesafeler
        distances = {node.id: float("inf") for node in self.nodes}
        previous = {node.id: None for node in self.nodes}

        distances[start_id] = 0
        unvisited = set(distances.keys())

        while unvisited:
            current = min(unvisited, key=lambda node_id: distances[node_id])
            unvisited.remove(current)

            if current == end_id:
                break

            current_node = self.get_node_by_id(current)
            for neighbor_id in current_node.komsular:
                if neighbor_id not in unvisited:
                    continue

                neighbor_node = self.get_node_by_id(neighbor_id)
                weight = self.calculate_weight(current_node, neighbor_node)
                new_dist = distances[current] + weight

                if new_dist < distances[neighbor_id]:
                    distances[neighbor_id] = new_dist
                    previous[neighbor_id] = current

        # Yol oluşturma
        path = []
        current = end_id
        while current is not None:
            path.insert(0, current)
            current = previous[current]

        if path[0] != start_id:
            raise ValueError("Bu iki node arasında yol yok")

        return path, distances[end_id]
    
        # =========================
    # A* (A-Star) En Kısa Yol
    # =========================
    def heuristic(self, node1: Node, node2: Node):
        # Basit ve tutarlı heuristic:
        # Özellik farklarına dayalı tahmin (küçük fark = yakın)
        return (
            abs(node1.aktiflik - node2.aktiflik)
            + abs(node1.etkilesim - node2.etkilesim)
            + abs(node1.baglanti_sayisi - node2.baglanti_sayisi)
        )

    def astar(self, start_id, end_id):
        start_node = self.get_node_by_id(start_id)
        end_node = self.get_node_by_id(end_id)

        if start_node is None or end_node is None:
            raise ValueError("Başlangıç veya hedef node bulunamadı")

        open_set = {start_id}
        came_from = {}

        g_score = {node.id: float("inf") for node in self.nodes}
        f_score = {node.id: float("inf") for node in self.nodes}

        g_score[start_id] = 0
        f_score[start_id] = self.heuristic(start_node, end_node)

        while open_set:
            current = min(open_set, key=lambda nid: f_score[nid])

            if current == end_id:
                # Yol oluştur
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.insert(0, current)
                return path, g_score[end_id]

            open_set.remove(current)
            current_node = self.get_node_by_id(current)

            for neighbor_id in current_node.komsular:
                neighbor_node = self.get_node_by_id(neighbor_id)
                tentative_g = g_score[current] + self.calculate_weight(
                    current_node, neighbor_node
                )

                if tentative_g < g_score[neighbor_id]:
                    came_from[neighbor_id] = current
                    g_score[neighbor_id] = tentative_g
                    f_score[neighbor_id] = tentative_g + self.heuristic(
                        neighbor_node, end_node
                    )
                    open_set.add(neighbor_id)

        raise ValueError("Bu iki node arasında yol yok")
    
    # =========================
    # Welsh–Powell Graph Coloring
    # =========================
    def welsh_powell(self):
        # Node'ları dereceye göre büyükten küçüğe sırala
        sorted_nodes = sorted(
            self.nodes,
            key=lambda n: n.baglanti_sayisi,
            reverse=True
        )

        color_of = {}   # node_id -> color_index
        current_color = 0

        for node in sorted_nodes:
            if node.id in color_of:
                continue

            color_of[node.id] = current_color

            for other in sorted_nodes:
                if other.id in color_of:
                    continue

                # Komşuların rengiyle çakışıyor mu?
                conflict = False
                for komsu in other.komsular:
                    if color_of.get(komsu) == current_color:
                        conflict = True
                        break

                if not conflict:
                    color_of[other.id] = current_color

            current_color += 1

        return color_of

    # =========================
    # Spring Layout (Fruchterman-Reingold)
    # =========================
    def spring_layout(self, width=1200, height=800, iterations=50):
        """
        Basit bir yay-kütle (Spring-Force) yerleşim algoritması.
        """
        import random
        import math
        
        nodes = self.nodes
        n = len(nodes)
        if n == 0: return {}
        if n == 1: return {nodes[0].id: (width/2, height/2)}

        # 1. Başlangıç pozisyonları (Rastgele)
        positions = {node.id: [random.uniform(100, width-100), random.uniform(100, height-100)] for node in nodes}
        
        # Sabitler
        area = width * height
        k = math.sqrt(area / n)
        
        t = width / 10 # Başlangıç sıcaklığı
        dt = t / (iterations + 1)

        for i in range(iterations):
            disp = {node.id: [0.0, 0.0] for node in nodes}

            # 2. İtme Kuvvetleri (Repulsive) - Herkes herkesi iter
            for v_node in nodes:
                v = v_node.id
                v_pos = positions[v]
                for u_node in nodes:
                    u = u_node.id
                    if u == v: continue
                    
                    u_pos = positions[u]
                    
                    delta_x = v_pos[0] - u_pos[0]
                    delta_y = v_pos[1] - u_pos[1]
                    dist = math.sqrt(delta_x*delta_x + delta_y*delta_y) or 0.01
                    
                    # Fr = k^2 / d
                    force = (k * k) / dist
                    disp[v][0] += (delta_x / dist) * force
                    disp[v][1] += (delta_y / dist) * force

            # 3. Çekme Kuvvetleri (Attractive) - Sadece bağlı olanlar
            for edge in self.edges:
                v = edge.source
                u = edge.target
                if v not in positions or u not in positions: continue
                
                v_pos = positions[v]
                u_pos = positions[u]
                
                delta_x = v_pos[0] - u_pos[0]
                delta_y = v_pos[1] - u_pos[1]
                dist = math.sqrt(delta_x*delta_x + delta_y*delta_y) or 0.01
                
                # Fa = d^2 / k
                force = (dist * dist) / k
                
                # v -> u çekilir
                disp[v][0] -= (delta_x / dist) * force
                disp[v][1] -= (delta_y / dist) * force
                
                # u -> v çekilir
                disp[u][0] += (delta_x / dist) * force
                disp[u][1] += (delta_y / dist) * force

            # 4. Pozisyon Güncelleme
            for node in nodes:
                v = node.id
                d_len = math.sqrt(disp[v][0]**2 + disp[v][1]**2) or 0.01
                
                # Sıcaklık ile sınırla
                step = min(d_len, t)
                
                positions[v][0] += (disp[v][0] / d_len) * step
                positions[v][1] += (disp[v][1] / d_len) * step
                
                # Sınırlar içinde tut
                positions[v][0] = min(width-50, max(50, positions[v][0]))
                positions[v][1] = min(height-50, max(50, positions[v][1]))

            # Soğutma
            t -= dt

        # Tuple olarak döndür
        return {nid: (pos[0], pos[1]) for nid, pos in positions.items()}
