import sys
import os

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QPen, QPainter, QColor
from PyQt5.QtWidgets import QSizePolicy


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

class DeleteEdgeDialog(QDialog):
    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph
        self.setWindowTitle("Edge Sil")
        self.setFixedSize(300, 160)

        layout = QVBoxLayout()

        self.node1_input = QLineEdit()
        self.node2_input = QLineEdit()

        layout.addWidget(QLabel("Node 1 ID"))
        layout.addWidget(self.node1_input)

        layout.addWidget(QLabel("Node 2 ID"))
        layout.addWidget(self.node2_input)

        btn_del = QPushButton("Sil")
        btn_del.clicked.connect(self.delete_edge)
        layout.addWidget(btn_del)

        self.setLayout(layout)

    def delete_edge(self):
        try:
            n1 = int(self.node1_input.text().strip())
            n2 = int(self.node2_input.text().strip())

            reply = QMessageBox.question(
                self,
                "Onay",
                f"Edge ({n1} - {n2}) silinsin mi?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

            self.graph.remove_edge(n1, n2)
            QMessageBox.information(self, "Başarılı", "Edge silindi.")
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
        self.scene.setBackgroundBrush(QBrush(QColor(245, 245, 245)))
        self.view = QGraphicsView(self.scene)
        self.view.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.view.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.view.setResizeAnchor(QGraphicsView.AnchorViewCenter)


        self.view.setRenderHint(QPainter.Antialiasing, True)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform, True)


        self.setWindowTitle("Sosyal Ağ Analizi Uygulaması")
        self.resize(1400, 850)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(280)

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

        btn_update_node = QPushButton("Node Güncelle")
        btn_update_node.clicked.connect(self.open_update_node)

        btn_delete_node = QPushButton("Node Sil")
        btn_delete_node.clicked.connect(self.open_delete_node)

        btn_delete_edge = QPushButton("Edge Sil")
        btn_delete_edge.clicked.connect(self.open_delete_edge)




        




        left_layout.addStretch()

        left_layout.addWidget(self.create_section_label("📌 Grafik İşlemleri"))
        left_layout.addWidget(btn_add_node)
        left_layout.addWidget(btn_update_node)
        left_layout.addWidget(btn_delete_node)
        left_layout.addWidget(btn_add_edge)
        left_layout.addWidget(btn_delete_edge)

        left_layout.addWidget(self.create_section_label("📊 Algoritmalar"))
        left_layout.addWidget(btn_bfs)
        left_layout.addWidget(btn_dfs)
        left_layout.addWidget(btn_dijkstra)
        left_layout.addWidget(btn_astar)
        left_layout.addWidget(btn_cc)

        left_layout.addWidget(self.create_section_label("📈 Analiz"))
        left_layout.addWidget(btn_top5)
        left_layout.addWidget(btn_color)

        left_layout.addWidget(self.create_section_label("💾 Veri"))
        left_layout.addWidget(btn_save)

        left_layout.addStretch()




        right_layout.addWidget(QLabel("Graf Çizim Alanı (Canvas)"))
        right_layout.addWidget(self.view) 

        main_layout.addWidget(left_widget)
        main_layout.addLayout(right_layout)

        main_layout.addLayout(right_layout, 5)


        central.setLayout(main_layout)

        self.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI';
            font-size: 13px;
        }

        QPushButton {
            background-color: #2E3440;
            color: white;
            border-radius: 6px;
            padding: 6px;
        }

        QPushButton:hover {
            background-color: #4C566A;
        }

        QLabel {
            font-weight: bold;
            margin-top: 8px;
        }
    """)


        self.draw_graph()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_scene()

    def fit_scene(self):
        if not self.scene.items():
            return

        rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(rect)
        self.view.fitInView(rect, Qt.KeepAspectRatio)

    def open_delete_edge(self):
        dialog = DeleteEdgeDialog(self.graph)
        if dialog.exec_():
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

    def open_update_node(self):
       dialog = UpdateNodeDialog(self.graph)
       if dialog.exec_():
        self.draw_graph()

    def open_delete_node(self):
       dialog = DeleteNodeDialog(self.graph)
       if dialog.exec_():
        self.draw_graph()
                  


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
        self.scene.clear()
        self.scene.setSceneRect(0, 0, 700, 500)
        self.draw_grid()


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

    # === MERKEZ VE PARAMETRELER ===
        center_x, center_y = 350, 250
        MAX_RADIUS = 220

        K_ETKILESIM = 12      # etkileşim → merkeze çekme
        K_BAGLANTI = 18       # bağlantı sayısı → merkeze çekme
        K_AKTIFLIK = 140      # aktiflik → yukarı taşıma

        n = len(self.graph.nodes)
        angle_step = 2 * math.pi / max(1, n)

        positions = {}

    # === NODE POZİSYONLARI (SEÇENEK 2) ===
        for i, node in enumerate(self.graph.nodes):
            radius = (
                MAX_RADIUS
                - node.etkilesim * K_ETKILESIM
                - node.baglanti_sayisi * K_BAGLANTI
        )

            radius = max(60, radius)  # merkeze yapışmasın

            angle = i * angle_step

            x = center_x + radius * math.cos(angle)
            y = (
                center_y
                + radius * math.sin(angle)
                - node.aktiflik * K_AKTIFLIK
        )

            positions[node.id] = QPointF(x, y)

    # === EDGE'LER ===
        for e in self.graph.edges:
            if e.source not in positions or e.target not in positions:
                continue

            p1 = positions[e.source]
            p2 = positions[e.target]

            edge_item = EdgeItem(e, p1, p2)
            self.scene.addItem(edge_item)
            self.scene.addItem(edge_item.label)


    # === NODE'LAR ===
        for node in self.graph.nodes:
            color_idx = colors.get(node.id, 0)
            color = palette[color_idx % len(palette)]
            pos = positions[node.id]

            item = NodeItem(node, pos.x(), pos.y(), color=color)
            self.scene.addItem(item)

            self.fit_scene()


    def draw_grid(self, step=40):
        pen = QPen(QColor(220, 220, 220))
        rect = self.scene.sceneRect()

        x = int(rect.left())
        while x < rect.right():
            self.scene.addLine(x, rect.top(), x, rect.bottom(), pen)
            x += step

        y = int(rect.top())
        while y < rect.bottom():
            self.scene.addLine(rect.left(), y, rect.right(), y, pen)
            y += step

    def create_section_label(self, text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setMinimumHeight(32)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 6px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
        """)
        return label







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


from PyQt5.QtWidgets import QGraphicsTextItem, QMessageBox
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, node, x, y, r=18, color=Qt.gray):
        super().__init__(0, 0, 2*r, 2*r)
        self.node = node
        self.setPos(x - r, y - r)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 2))
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)

        self.setAcceptHoverEvents(True)
        self.setToolTip(
            f"ID: {node.id}\n"
            f"İsim: {node.name}\n"
            f"Aktiflik: {node.aktiflik}\n"
            f"Etkileşim: {node.etkilesim}\n"
            f"Bağlantı Sayısı: {node.baglanti_sayisi}"
        )   

        label = QGraphicsTextItem(str(node.id), self)
        label.setDefaultTextColor(Qt.white)
        label.setPos(r / 2, r / 2)

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


    
    def hoverEnterEvent(self, event):
        self.setPen(QPen(Qt.yellow, 3))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.isSelected():
            self.setPen(QPen(Qt.black, 2))
        super().hoverLeaveEvent(event)

class EdgeItem(QGraphicsLineItem):
    def __init__(self, edge, p1: QPointF, p2: QPointF):
        super().__init__(p1.x(), p1.y(), p2.x(), p2.y())

        self.edge = edge
        self.setZValue(-1)  # node'ların altında kalsın
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsLineItem.ItemIsSelectable, True)

        thickness = 1 + edge.weight * 6
        self.default_pen = QPen(Qt.black, thickness)
        self.hover_pen = QPen(Qt.darkYellow, thickness + 1)
        self.selected_pen = QPen(Qt.red, thickness + 2)

        self.setPen(self.default_pen)
        self.setToolTip(
            f"Edge\n"
            f"{edge.source} ↔ {edge.target}\n"
            f"Ağırlık: {edge.weight:.4f}"
        )


        # Ağırlık etiketi
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2

        self.label = QGraphicsTextItem(f"{edge.weight:.2f}")
        self.label.setDefaultTextColor(Qt.darkGray)
        self.label.setPos(mid_x, mid_y)

    def hoverEnterEvent(self, event):
        self.setPen(self.hover_pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.isSelected():
            self.setPen(self.default_pen)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        scene = self.scene()
        if scene:
            scene.clearSelection()
        self.setSelected(True)
        self.setPen(self.selected_pen)

        QMessageBox.information(
            None,
            "Edge Bilgisi",
            f"{self.edge.source} ↔ {self.edge.target}\n"
            f"Ağırlık: {self.edge.weight:.4f}"
        )

        super().mousePressEvent(event)

class UpdateNodeDialog(QDialog):
    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph
        self.setWindowTitle("Node Güncelle")
        self.setFixedSize(350, 260)

        layout = QVBoxLayout()

        self.id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.aktiflik_input = QLineEdit()
        self.etkilesim_input = QLineEdit()

        layout.addWidget(QLabel("Güncellenecek Node ID"))
        layout.addWidget(self.id_input)

        layout.addWidget(QLabel("Yeni İsim (boş bırakabilirsin)"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Yeni Aktiflik (0-1) (boş bırakabilirsin)"))
        layout.addWidget(self.aktiflik_input)

        layout.addWidget(QLabel("Yeni Etkileşim (boş bırakabilirsin)"))
        layout.addWidget(self.etkilesim_input)

        btn_update = QPushButton("Güncelle")
        btn_update.clicked.connect(self.update_node)
        layout.addWidget(btn_update)

        self.setLayout(layout)

    def update_node(self):
        try:
            node_id = int(self.id_input.text().strip())

            name = self.name_input.text().strip()
            name = name if name else None

            aktiflik_txt = self.aktiflik_input.text().strip()
            aktiflik = float(aktiflik_txt) if aktiflik_txt else None
            if aktiflik is not None and not (0 <= aktiflik <= 1):
                raise ValueError("Aktiflik 0 ile 1 arasında olmalı")

            etkilesim_txt = self.etkilesim_input.text().strip()
            etkilesim = int(etkilesim_txt) if etkilesim_txt else None

            self.graph.update_node(node_id, name=name, aktiflik=aktiflik, etkilesim=etkilesim)
            QMessageBox.information(self, "Başarılı", "Node güncellendi.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))  

class DeleteNodeDialog(QDialog):
    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph
        self.setWindowTitle("Node Sil")
        self.setFixedSize(300, 140)

        layout = QVBoxLayout()

        self.id_input = QLineEdit()
        layout.addWidget(QLabel("Silinecek Node ID"))
        layout.addWidget(self.id_input)

        btn_del = QPushButton("Sil")
        btn_del.clicked.connect(self.delete_node)
        layout.addWidget(btn_del)

        self.setLayout(layout)

    def delete_node(self):
        try:
            node_id = int(self.id_input.text().strip())

            # emin olmak için ufak onay
            reply = QMessageBox.question(
                self,
                "Onay",
                f"Node {node_id} silinsin mi?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

            self.graph.remove_node(node_id)
            QMessageBox.information(self, "Başarılı", "Node silindi.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))







# =========================
# PROGRAM BAŞLAT
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

    print("NodeItem =", NodeItem)
