import sys

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

        left_layout.addWidget(QLabel("Kontrol Paneli"))
        left_layout.addWidget(btn_add_node)
        left_layout.addWidget(btn_add_edge)
        left_layout.addWidget(btn_bfs)
        left_layout.addWidget(btn_dfs)
        left_layout.addWidget(btn_save)
        left_layout.addWidget(btn_cc)
        left_layout.addWidget(btn_top5)


        left_layout.addStretch()

        right_layout.addWidget(QLabel("Graf Çizim Alanı (Canvas)"))

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)

        central.setLayout(main_layout)

    # =========================
    # ACTIONS
    # =========================
    def open_add_node(self):
        AddNodeDialog(self.graph).exec_()

    def open_add_edge(self):
        AddEdgeDialog(self.graph).exec_()

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
        text = "\n".join([f"{i+1}. bileşen: {c}" for i, c in enumerate(comps)])

        QMessageBox.information(self, "Bağlı Bileşenler", text)


    def save_json(self):
        self.graph.save_to_json(self.graph.data_path)
        QMessageBox.information(self, "Kaydedildi", "JSON kaydedildi.")


# =========================
# PROGRAM BAŞLAT
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
