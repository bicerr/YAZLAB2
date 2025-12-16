import sys
import os

# ui/src klasörünü Python path'e ekle
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QDialog
)

from graph import Graph
from node import Node


# =========================
# NODE EKLE DIALOG
# =========================
class AddNodeDialog(QDialog):
    def __init__(self, graph: Graph):
        super().__init__()
        self.graph = graph
        self.setWindowTitle("Node Ekle")
        self.setMinimumSize(360, 280)

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

        layout.addSpacing(10)
        layout.addWidget(btn_add)

        self.setLayout(layout)

    def add_node(self):
        try:
            if not all([
                self.id_input.text().strip(),
                self.name_input.text().strip(),
                self.aktiflik_input.text().strip(),
                self.etkilesim_input.text().strip()
            ]):
                raise ValueError("Tüm alanlar doldurulmalıdır.")

            node_id = int(self.id_input.text())
            aktiflik = float(self.aktiflik_input.text())
            etkilesim = int(self.etkilesim_input.text())

            if not (0 <= aktiflik <= 1):
                raise ValueError("Aktiflik 0 ile 1 arasında olmalı.")

            node = Node(
                node_id,
                self.name_input.text(),
                aktiflik,
                etkilesim,
                0,
                []
            )

            self.graph.add_node(node)
            QMessageBox.information(self, "Başarılı", "Node başarıyla eklendi.")
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
        self.resize(1000, 600)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        btn_add_node = QPushButton("Node Ekle")
        btn_add_node.clicked.connect(self.open_add_node)

        btn_edge = QPushButton("Edge Ekle")
        btn_bfs = QPushButton("BFS Çalıştır")
        btn_dfs = QPushButton("DFS Çalıştır")

        btn_save = QPushButton("JSON Kaydet")
        btn_save.clicked.connect(self.save_json)

        left_layout.addWidget(QLabel("<b>Kontrol Paneli</b>"))
        left_layout.addWidget(btn_add_node)
        left_layout.addWidget(btn_edge)
        left_layout.addWidget(btn_bfs)
        left_layout.addWidget(btn_dfs)
        left_layout.addWidget(btn_save)
        left_layout.addStretch()

        right_layout.addWidget(QLabel("Graf Çizim Alanı (Canvas)"))
        right_layout.addStretch()

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)

        central.setLayout(main_layout)

    def open_add_node(self):
        dialog = AddNodeDialog(self.graph)
        dialog.exec_()

    def save_json(self):
        self.graph.save_to_json("data/graph.json")
        QMessageBox.information(self, "Kaydedildi", "Graph JSON dosyasına kaydedildi.")


# =========================
# PROGRAM BAŞLAT
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 🔥 Görünümü düzeltir
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
