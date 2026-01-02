import json
import os
from collections import deque

from .node import Node
from .edge import Edge


class Graph:
    def __init__(self, data_path=None, autosave=False):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_path = data_path or os.path.join(base_dir, "data", "graph.json")
        self.autosave = autosave

        self.nodes = []
        self.edges = []

        if os.path.exists(self.data_path):
            self.load_from_json(self.data_path)

    
    def load_from_csv(self, path):
        import csv
        self.nodes = []
        self.edges = []
        
        # Format: DugumId, Ozellik_I (Aktiflik), Ozellik_II (Etkilesim), Ozellik_III (Baglanti), Komsular
        # Delimiters can be comma or semicolon usually. We'll try to sniff or just assume standard CSV.
        
        nodes_dict = {}
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                # Read all lines to handle potential format issues manually
                lines = f.readlines()
                
            # Skip header if present (check if first char is not digit)
            start_idx = 0
            if lines and not lines[0][0].isdigit():
                start_idx = 1
                
            # First pass: Create Nodes
            for line in lines[start_idx:]:
                line = line.strip()
                if not line: continue
                
                # Handle potential delimiters
                parts = line.replace(';', ',').split(',')
                # Filter empty strings from split (e.g. trailing comma)
                parts = [p.strip() for p in parts if p.strip()]
                
                if len(parts) < 5: continue
                
                try:
                    nid = int(parts[0])
                    act = float(parts[1])
                    inter = int(parts[2])
                    # parts[3] is listed connection count, but we recalculate it usually or store it.
                    # We will store it for weight calculation base.
                    conn_count_val = int(parts[3]) 
                    
                    # Remaining parts are neighbors
                    # Some inputs might have neighbors joined by spaces or specific format.
                    # Standard requirement: "2,4,5"
                    # But splitting by comma above might have split the neighbors too if they weren't quoted.
                    # Let's re-parse neighbors carefully.
                    # If parts were split by comma: [id, act, inter, count, n1, n2, n3...]
                    neighbors_raw = parts[4:]
                    neighbors = []
                    for n_str in neighbors_raw:
                        if n_str.isdigit():
                            neighbors.append(int(n_str))
                            
                    node = Node(nid, f"Node {nid}", act, inter, conn_count_val, neighbors)
                    # Note: We pass neighbors to constructor if supported, otherwise attribute
                    # Node definition in this codebase seemed to take (id, name, act, inter) initially?
                    # Let's check Node __init__ signature usage in previous code:
                    # Node(nid, f"Node {nid}", act, inter) -> checking file outline/content helps.
                    # Looking at line 33 of original file: n = Node(nid, f"Node {nid}", act, inter)
                    # And line 73: n["komsular"] passed to constructor? 
                    # Let's be safe and set attributes.
                    
                    # The original load_from_json passed 6 args. Let's check Node class definition?
                    # I'll just assign to .komsular to be safe.
                    node.komsular = neighbors
                    
                    self.nodes.append(node)
                    nodes_dict[nid] = node
                except ValueError:
                    continue

            # Second pass: Create Edges
            # We don't want duplicate edges (1-2 and 2-1).
            added_pairs = set()
            
            for node in self.nodes:
                for neighbor_id in node.komsular:
                    if neighbor_id not in nodes_dict:
                        continue
                        
                    n1 = node
                    n2 = nodes_dict[neighbor_id]
                    
                    # Sort to check uniqueness
                    pair = tuple(sorted((n1.id, n2.id)))
                    if pair in added_pairs:
                        continue
                        
                    if n1.id == n2.id: continue # No self loops
                    
                    # Calculate weight
                    w = self.calculate_weight(n1, n2)
                    self.edges.append(Edge(n1.id, n2.id, w))
                    added_pairs.add(pair)
            
            # Recalculate connection counts if we want to ensure consistency with loaded edges,
            # but the requirement says "Use the table". The table had a connection count column.
            # Using the loaded 'baglanti_sayisi' for the weight formula as per requirement.
            
            self._autosave()
            
        except Exception as e:
            print(f"Error loading CSV: {e}")


   
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

    def export_adjacency_matrix(self, path):
        sorted_nodes = sorted(self.nodes, key=lambda n: n.id)
        node_ids = [n.id for n in sorted_nodes]
        n_count = len(node_ids)
        
        
        matrix = []
        header = [""] + [str(nid) for nid in node_ids]
        matrix.append(header)
        
        for i, r_node in enumerate(sorted_nodes):
            row = [str(r_node.id)]
            for c_node in sorted_nodes:
                val = "0"
                if self.edge_exists(r_node.id, c_node.id):
                   val = "1"
                row.append(val)
            matrix.append(row)
            
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(matrix)

    def _autosave(self):
        if self.autosave and self.data_path:
            self.save_to_json(self.data_path)

    
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

    
    def calculate_weight(self, node1: Node, node2: Node):
        return 1 / (
            1
            + (node1.aktiflik - node2.aktiflik) ** 2
            + (node1.etkilesim - node2.etkilesim) ** 2
            + (node1.baglanti_sayisi - node2.baglanti_sayisi) ** 2
        )

    
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

        if target_id not in node1.komsular:
            node1.komsular.append(target_id)
        if source_id not in node2.komsular:
            node2.komsular.append(source_id)

        node1.baglanti_sayisi = len(node1.komsular)
        node2.baglanti_sayisi = len(node2.komsular)

        self._autosave()
        
    def remove_edge(self, source_id, target_id):
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

        n1 = self.get_node_by_id(source_id)
        n2 = self.get_node_by_id(target_id)

        if n1 and target_id in n1.komsular:
            n1.komsular.remove(target_id)
            n1.baglanti_sayisi = len(n1.komsular)

        if n2 and source_id in n2.komsular:
            n2.komsular.remove(source_id)
            n2.baglanti_sayisi = len(n2.komsular)

        self._autosave()



        

    
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
    
       
    def connected_components(self, threshold=0.0):
        """
        Finds connected components.
        If threshold > 0, edges with weight < threshold are ignored (treated as not connected).
        This allows for community detection based on strong structural/attribute similarities.
        """
        visited = set()
        components = []

        for node in self.nodes:
            if node.id in visited:
                continue

            comp = []
            stack = [node.id]
            visited.add(node.id)

            while stack:
                current_id = stack.pop()
                comp.append(current_id)

                current_node = self.get_node_by_id(current_id)
                if current_node is None:
                    continue

                for nb_id in current_node.komsular:
                    # Check if edge satisfies threshold
                    # We need to find the edge object to get the weight
                    edge_w = 0
                    for e in self.edges:
                        if (e.source == current_id and e.target == nb_id) or \
                           (e.source == nb_id and e.target == current_id):
                            edge_w = e.weight
                            break
                    
                    if edge_w < threshold:
                        continue

                    if nb_id not in visited:
                        visited.add(nb_id)
                        stack.append(nb_id)

            components.append(comp)

        return components


               
    def degree_centrality_top5(self):
        degrees = [(n.id, len(n.komsular)) for n in self.nodes]

        degrees.sort(key=lambda x: x[1], reverse=True)

        return degrees[:5]

    
    def dijkstra(self, start_id, end_id):
        if self.get_node_by_id(start_id) is None or self.get_node_by_id(end_id) is None:
            raise ValueError("Başlangıç veya hedef node bulunamadı")

        
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
                weight_val = self.calculate_weight(current_node, neighbor_node)
                cost = 1.0 / weight_val if weight_val > 0 else float('inf')
                
                new_dist = distances[current] + cost

                if new_dist < distances[neighbor_id]:
                    distances[neighbor_id] = new_dist
                    previous[neighbor_id] = current

        path = []
        current = end_id
        while current is not None:
            path.insert(0, current)
            current = previous[current]

        if path[0] != start_id:
            raise ValueError("Bu iki node arasında yol yok")

        return path, distances[end_id]
    
       
    def heuristic(self, node1: Node, node2: Node):
        
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
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.insert(0, current)
                return path, g_score[end_id]

            open_set.remove(current)
            current_node = self.get_node_by_id(current)

            for neighbor_id in current_node.komsular:
                neighbor_node = self.get_node_by_id(neighbor_id)
                
                weight_val = self.calculate_weight(current_node, neighbor_node)
                cost = 1.0 / weight_val if weight_val > 0 else float('inf')
                
                tentative_g = g_score[current] + cost

                if tentative_g < g_score[neighbor_id]:
                    came_from[neighbor_id] = current
                    g_score[neighbor_id] = tentative_g
                    f_score[neighbor_id] = tentative_g + self.heuristic(
                        neighbor_node, end_node
                    )
                    open_set.add(neighbor_id)

        raise ValueError("Bu iki node arasında yol yok")
    
    
    def welsh_powell(self, threshold=0.0):
        sorted_nodes = sorted(
            self.nodes,
            key=lambda n: n.baglanti_sayisi,
            reverse=True
        )

        color_of = {}   
        current_color = 0

        for node in sorted_nodes:
            if node.id in color_of:
                continue

            color_of[node.id] = current_color

            for other in sorted_nodes:
                if other.id in color_of:
                    continue

                conflict = False
                for komsu in other.komsular:
                    # Check if neighbor has current color
                    if color_of.get(komsu) == current_color:
                        # Check if the edge is 'active' based on threshold
                        # We need to verify weight.
                        w = 0
                        # Optimization: We could pre-index edges, but for N=100 iteration is fine.
                        for e in self.edges:
                             if (e.source == other.id and e.target == komsu) or \
                                (e.source == komsu and e.target == other.id):
                                 w = e.weight
                                 break
                        
                        if w >= threshold:
                            conflict = True
                            break

                if not conflict:
                    color_of[other.id] = current_color

            current_color += 1

        return color_of

   
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

        positions = {node.id: [random.uniform(100, width-100), random.uniform(100, height-100)] for node in nodes}
        
        area = width * height
        k = math.sqrt(area / n)
        
        t = width / 10 
        dt = t / (iterations + 1)

        for i in range(iterations):
            disp = {node.id: [0.0, 0.0] for node in nodes}

            
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
                    
                    force = (k * k) / dist
                    disp[v][0] += (delta_x / dist) * force
                    disp[v][1] += (delta_y / dist) * force

            for edge in self.edges:
                v = edge.source
                u = edge.target
                if v not in positions or u not in positions: continue
                
                v_pos = positions[v]
                u_pos = positions[u]
                
                delta_x = v_pos[0] - u_pos[0]
                delta_y = v_pos[1] - u_pos[1]
                dist = math.sqrt(delta_x*delta_x + delta_y*delta_y) or 0.01
                
                force = (dist * dist) / k
                
                disp[v][0] -= (delta_x / dist) * force
                disp[v][1] -= (delta_y / dist) * force
                
                disp[u][0] += (delta_x / dist) * force
                disp[u][1] += (delta_y / dist) * force

            for node in nodes:
                v = node.id
                d_len = math.sqrt(disp[v][0]**2 + disp[v][1]**2) or 0.01
                
                step = min(d_len, t)
                
                positions[v][0] += (disp[v][0] / d_len) * step
                positions[v][1] += (disp[v][1] / d_len) * step
                
                positions[v][0] = min(width-50, max(50, positions[v][0]))
                positions[v][1] = min(height-50, max(50, positions[v][1]))

            t -= dt

        return {nid: (pos[0], pos[1]) for nid, pos in positions.items()}
