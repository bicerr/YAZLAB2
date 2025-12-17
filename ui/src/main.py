import sys
import os

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen, QPainter

import math


from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QDialog
)

from ui.src.graph import Graph
from ui.src.node import Node


# =========================
# NODE EKLE DIALOG
# =========================
class AddNodeDialog(QDialog):
    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph
        self.setWindowTitle("Node Ekle")
        self.setFixedSize(350, 300)

        layout = QVBoxLayout()

        self.id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.aktiflik_input = QLineEdit()
        self.etkilesim_input = QLineEdit()

        layout.addWidget(QLabel("Node ID"))
        layout.addWidget(self.id_input)

        layout.addWidget(QLabel("İsim"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Aktiflik (0-1)"))
        layout.addWidget(self.aktiflik_input)

        layout.addWidget(QLabel("Etkileşim"))
        layout.addWidget(self.etkilesim_input)

        btn_add = QPushButton("Ekle")
        btn_add.clicked.connect(self.add_node)

        layout.addWidget(btn_add)
        self.setLayout(layout)

    def add_node(self):
        try:
            node_id = int(self.id_input.text())
            aktiflik = float(self.aktiflik_input.text())
            etkilesim = int(self.etkilesim_input.text())

            node = Node(
                node_id,
                self.name_input.text(),
                aktiflik,
                etkilesim
            )

            self.graph.add_node(node)
            QMessageBox.information(self, "Başarılı", "Node eklendi.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))


# =========================
# EDGE EKLE DIALOG
# =========================
class AddEdgeDialog(QDialog):
    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph
        self.setWindowTitle("Edge Ekle")
        self.setFixedSize(300, 180)

        layout = QVBoxLayout()

        self.node1_input = QLineEdit()
        self.node2_input = QLineEdit()

        layout.addWidget(QLabel("Node 1 ID"))
        layout.addWidget(self.node1_input)

        layout.addWidget(QLabel("Node 2 ID"))
        layout.addWidget(self.node2_input)

        btn_add = QPushButton("Ekle")
        btn_add.clicked.connect(self.add_edge)

        layout.addWidget(btn_add)
        self.setLayout(layout)

    def add_edge(self):
        try:
            n1 = int(self.node1_input.text())
            n2 = int(self.node2_input.text())

            self.graph.add_edge(n1, n2)
            QMessageBox.information(self, "Başarılı", "Edge eklendi")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))


# =========================
# ANA PENCERE
# =========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.graph = Graph()
        from PyQt5.QtGui import QPainter
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing, True)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform, True)


        self.setWindowTitle("Sosyal Ağ Analizi Uygulaması")
        self.setFixedSize(1000, 600)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        btn_add_node = QPushButton("Node Ekle")
        btn_add_node.clicked.connect(self.open_add_node)

        btn_add_edge = QPushButton("Edge Ekle")
        btn_add_edge.clicked.connect(self.open_add_edge)

        btn_bfs = QPushButton("BFS Çalıştır")
        btn_bfs.clicked.connect(self.run_bfs)

        btn_dfs = QPushButton("DFS Çalıştır")
        btn_dfs.clicked.connect(self.run_dfs)

        btn_save = QPushButton("JSON Kaydet")
        btn_save.clicked.connect(self.save_json)

        btn_cc = QPushButton("Bileşenleri Bul")
        btn_cc.clicked.connect(self.show_components)

        btn_top5 = QPushButton("En Etkili 5 Kullanıcı")
        btn_top5.clicked.connect(self.show_top5)

        btn_dijkstra = QPushButton("Dijkstra (En Kısa Yol)")
        btn_dijkstra.clicked.connect(self.open_dijkstra)

        btn_astar = QPushButton("A* (En Kısa Yol)")
        btn_astar.clicked.connect(self.open_astar)

        btn_color = QPushButton("Graf Renklendir (Welsh–Powell)")
        btn_color.clicked.connect(self.run_coloring)

        left_layout.addWidget(QLabel("Kontrol Paneli"))
        left_layout.addWidget(btn_add_node)
        left_layout.addWidget(btn_add_edge)
        left_layout.addWidget(btn_bfs)
        left_layout.addWidget(btn_dfs)
        left_layout.addWidget(btn_save)
        left_layout.addWidget(btn_cc)
        left_layout.addWidget(btn_top5)
        left_layout.addWidget(btn_dijkstra)
        left_layout.addWidget(btn_astar)
        left_layout.addWidget(btn_color)



        left_layout.addStretch()

        right_layout.addWidget(QLabel("Graf Çizim Alanı (Canvas)"))
        right_layout.addWidget(self.view) 

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)

        central.setLayout(main_layout)

        self.draw_graph()

    # =========================
    # ACTIONS
    # =========================
    def open_add_node(self):
      dialog = AddNodeDialog(self.graph)
      if dialog.exec_():        
        self.draw_graph()     


    def open_add_edge(self):
      dialog = AddEdgeDialog(self.graph)
      if dialog.exec_():        
        self.draw_graph()


    def open_dijkstra(self):
       dialog = DijkstraDialog(self.graph)
       dialog.exec_()           


    def open_astar(self):
       dialog = AStarDialog(self.graph)
       dialog.exec_()            


    def run_bfs(self):
        if not self.graph.nodes:
            QMessageBox.warning(self, "Uyarı", "Graf boş.")
            return

        start = self.graph.nodes[0].id
        result = self.graph.bfs(start)

        QMessageBox.information(
            self, "BFS Sonucu",
            " -> ".join(map(str, result))
        )

    def run_dfs(self):
        if not self.graph.nodes:
            QMessageBox.warning(self, "Uyarı", "Graf boş.")
            return

        start = self.graph.nodes[0].id
        result = self.graph.dfs(start)

        QMessageBox.information(
            self, "DFS Sonucu",
            " -> ".join(map(str, result))
        )
    def show_top5(self):
        top5 = self.graph.degree_centrality_top5()

        if not top5:
            QMessageBox.information(self, "Sonuç", "Graf boş.")
            return

        lines = []
        for i, (node_id, degree) in enumerate(top5, start=1):
            lines.append(f"{i}. Node ID: {node_id}  |  Derece: {degree}")

        QMessageBox.information(
            self,
            "Degree Centrality - Top 5",
            "\n".join(lines)
        )

    def show_components(self):
        comps = self.graph.connected_components()

        if not comps:
           QMessageBox.information(self, "Bağlı Bileşenler", "Graf boş veya bileşen bulunamadı.")
           return

        text = "\n".join([f"{i+1}. bileşen: {c}" for i, c in enumerate(comps)])
        QMessageBox.information(self, "Bağlı Bileşenler", text)


    def save_json(self):
        self.graph.save_to_json(self.graph.data_path)
        QMessageBox.information(self, "Kaydedildi", "JSON kaydedildi.")

    def run_coloring(self):
        try:
            colors = self.graph.welsh_powell()

            # Renk isimleri (rapor + kullanıcı için)
            color_names = [
                "Kırmızı", "Mavi", "Yeşil", "Sarı",
                "Mor", "Turuncu", "Pembe", "Kahverengi"
            ]

            lines = []
            for node_id, color_index in colors.items():
                color_name = color_names[color_index % len(color_names)]
                lines.append(f"Node {node_id} → {color_name}")

            QMessageBox.information(
                self,
                "Welsh–Powell Renklendirme",
                "\n".join(lines)
            )

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def draw_graph(self):
        self.scene.clear()

        if not self.graph.nodes:
            return

        # Welsh–Powell renkleri
        try:
            colors = self.graph.welsh_powell()
        except:
            colors = {}

        palette = [
            Qt.red, Qt.blue, Qt.green, Qt.yellow,
            Qt.magenta, Qt.cyan, Qt.darkRed, Qt.darkBlue
        ]

        # Daire düzeni
        cx, cy = 350, 250
        radius = 180
        n = len(self.graph.nodes)
        positions = {}

        for i, node in enumerate(self.graph.nodes):
            angle = 2 * math.pi * i / n
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            positions[node.id] = QPointF(x, y)

        # Edge’ler
        pen = QPen(Qt.black, 2)

        for e in self.graph.edges:
            p1 = positions[e.source]
            p2 = positions[e.target]

            line = QGraphicsLineItem(p1.x(), p1.y(), p2.x(), p2.y())
            line.setPen(pen)


            line.setAcceptedMouseButtons(Qt.NoButton)

   
            line.setZValue(-1)

            self.scene.addItem(line)


        # Node’lar
        for node in self.graph.nodes:
            color_idx = colors.get(node.id, 0)
            color = palette[color_idx % len(palette)]
            pos = positions[node.id]
            item = NodeItem(node, pos.x(), pos.y(), color=color)
            self.scene.addItem(item)




class DijkstraDialog(QDialog):
    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph
        self.setWindowTitle("Dijkstra - En Kısa Yol")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.start_input = QLineEdit()
        self.end_input = QLineEdit()

        layout.addWidget(QLabel("Başlangıç Node ID"))
        layout.addWidget(self.start_input)

        layout.addWidget(QLabel("Hedef Node ID"))
        layout.addWidget(self.end_input)

        btn_run = QPushButton("Hesapla")
        btn_run.clicked.connect(self.run_dijkstra)
        

        layout.addWidget(btn_run)
        self.setLayout(layout)

    def run_dijkstra(self):
        try:
            start = int(self.start_input.text())
            end = int(self.end_input.text())

            path, cost = self.graph.dijkstra(start, end)

            QMessageBox.information(
                self,
                "En Kısa Yol",
                f"Yol: {' -> '.join(map(str, path))}\nToplam Maliyet: {cost:.4f}"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))


class AStarDialog(QDialog):
    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph
        self.setWindowTitle("A* (A-Star) En Kısa Yol")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.start_input = QLineEdit()
        self.end_input = QLineEdit()

        layout.addWidget(QLabel("Başlangıç Node ID"))
        layout.addWidget(self.start_input)

        layout.addWidget(QLabel("Hedef Node ID"))
        layout.addWidget(self.end_input)

        btn_run = QPushButton("Hesapla")
        btn_run.clicked.connect(self.run_astar)

        layout.addWidget(btn_run)
        self.setLayout(layout)

    def run_astar(self):
        try:
            start = int(self.start_input.text())
            end = int(self.end_input.text())

            path, cost = self.graph.astar(start, end)

            QMessageBox.information(
                self,
                "A* Sonucu",
                f"Yol: {' -> '.join(map(str, path))}\nToplam Maliyet: {cost:.4f}"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))



class NodeItem(QGraphicsEllipseItem):
    def __init__(self, node, x, y, r=18, color=Qt.gray):
        super().__init__(0, 0, 2*r, 2*r)
        self.node = node
        self.setPos(x - r, y - r)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 2))
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        scene = self.scene()
        if scene:
            scene.clearSelection()
        self.setSelected(True)

        QMessageBox.information(
            None,
            "Node Bilgisi",
            f"ID: {self.node.id}\n"
            f"İsim: {self.node.name}\n"
            f"Aktiflik: {self.node.aktiflik}\n"
            f"Etkileşim: {self.node.etkilesim}\n"
            f"Bağlantı Sayısı: {self.node.baglanti_sayisi}"
        )
        super().mousePressEvent(event)






# =========================
# PROGRAM BAŞLAT
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

    print("NodeItem =", NodeItem)
