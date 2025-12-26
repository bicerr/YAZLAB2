import sys
import os
import math

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QDialog, 
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QGraphicsTextItem, QScrollArea, QGraphicsItem, QComboBox, QFileDialog
)
from PyQt5.QtGui import QBrush, QPen, QPainter, QColor, QFont, QRadialGradient
from PyQt5.QtCore import Qt, QPointF, pyqtSignal

# Fix for module search path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.src.graph import Graph
from ui.src.node import Node
from ui.src.edge import Edge
from ui.src.styles import (
    COLORS, MAIN_APP_STYLE, HEADER_STYLE, PANEL_STYLE, 
    BUTTON_STYLE, INPUT_STYLE, TABLE_STYLE
)

# =========================
# UTILS & WIDGETS
# =========================
class Panel(QFrame):
    def __init__(self, title=None):
        super().__init__()
        self.setObjectName("Panel")
        self.setStyleSheet(PANEL_STYLE)
        
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setContentsMargins(10, 10, 10, 10)
        self.layout_main.setSpacing(10)
        
        if title:
            lbl = QLabel(title)
            lbl.setObjectName("PanelTitle")
            self.layout_main.addWidget(lbl)

    def add_widget(self, widget):
        self.layout_main.addWidget(widget)
        
    def add_layout(self, layout):
        self.layout_main.addLayout(layout)

class GlossyButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet(BUTTON_STYLE)
        self.setCursor(Qt.PointingHandCursor)

# =========================
# GRAPHICS ITEMS
# =========================
class NodeItem(QGraphicsEllipseItem):
    def __init__(self, node, x, y, r=22, color="#4cc9f0"):
        super().__init__(0, 0, 2*r, 2*r)
        self.node = node
        self.setPos(x - r, y - r)
        
        # Gradient Fill
        c = QColor(color)
        grad = QRadialGradient(r, r, r)
        grad.setColorAt(0, c.lighter(130))
        grad.setColorAt(1, c)
        
        self.setBrush(QBrush(grad))
        self.setPen(QPen(Qt.white, 2))
        
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Shadow Effect (Simulated via Z and darker circle behind? - Simplified here)
        
        # Label (ID) - Center
        # For 'Sosialex' maybe show icon? Let's just show ID clearly
        label = QGraphicsTextItem(str(node.id), self)
        label.setDefaultTextColor(Qt.white)
        font = QFont("Segoe UI", 10, QFont.Bold)
        label.setFont(font)
        rect = label.boundingRect()
        label.setPos(r - rect.width()/2, r - rect.height()/2)

    def hoverEnterEvent(self, event):
        self.setPen(QPen(QColor(COLORS["accent_cyan"]), 4))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.isSelected():
            self.setPen(QPen(Qt.white, 2))
        super().hoverLeaveEvent(event)
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            if value:
                self.setPen(QPen(QColor(COLORS["accent_blue"]), 4))
            else:
                self.setPen(QPen(Qt.white, 2))
        return super().itemChange(change, value)

class EdgeItem(QGraphicsLineItem):
    def __init__(self, edge, p1: QPointF, p2: QPointF):
        super().__init__(p1.x(), p1.y(), p2.x(), p2.y())
        self.setZValue(-1)
        w = max(1, min(6, edge.weight * 3))
        
        pen = QPen(QColor(COLORS["text_muted"]), w)
        pen.setCapStyle(Qt.RoundCap)
        self.setPen(pen)
        
        # Tooltip
        self.setAcceptHoverEvents(True)
        self.setToolTip(f"Edge: {edge.source}-{edge.target}\nAğırlık: {edge.weight:.4f}")

        # Text Label (Visual)
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2
        
        self.text = QGraphicsTextItem(f"{edge.weight:.2f}", self)
        # Center the text
        rect = self.text.boundingRect()
        self.text.setPos(mid_x - rect.width()/2, mid_y - rect.height()/2)
        
        # Style
        self.text.setDefaultTextColor(QColor("#a5b4fc")) # Light Indigo
        font = QFont("Arial", 9)
        self.text.setFont(font)
        
        # Background for text
        # (Optional: could add a rect behind, but let's try simple text first to avoid clutter)

# =========================
# MAIN WINDOW
# =========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sosialex - Sosyal Ağ Analizi")
        self.resize(1450, 900)
        # self.setStyleSheet(MAIN_APP_STYLE)  <-- Moved to main for global scope
        
        self.graph = Graph()
        self.is_colored = False  # Track if coloring should be applied
        
        # Main Layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # header
        self.create_header(main_layout)
        
        # Body
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(10, 10, 10, 10)
        body_layout.setSpacing(10)
        main_layout.addLayout(body_layout)
        
        # LEFT COL
        self.create_left_col(body_layout)
        
        # CENTER COL
        self.create_center_col(body_layout)
        
        # RIGHT COL
        self.create_right_col(body_layout)
        
        # Initial Draw
        self.draw_graph()

    def create_header(self, parent_layout):
        header = QFrame()
        header.setObjectName("Header")
        header.setStyleSheet(HEADER_STYLE)
        header.setFixedHeight(60)
        
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)
        
        # Centered Logo/Text
        hl.addStretch() # Push title to center
        title = QLabel("◇ Sosialex  ||  Sosyal Ağ Analizi Uygulaması")
        title.setObjectName("AppTitle")
        title.setAlignment(Qt.AlignCenter)
        hl.addWidget(title)
        hl.addStretch() # Push icons to right
        
        # Dummy system icons
        sys_icons = QLabel("🎥 🎤 ⚙️ ★")
        sys_icons.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 16px;")
        hl.addWidget(sys_icons)
        
        parent_layout.addWidget(header)

    def create_left_col(self, parent_layout):
        container = QWidget()
        container.setFixedWidth(260)
        l = QVBoxLayout(container)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(10)
        
        # 1. Graf İşlemleri
        p1 = Panel("Graf İşlemleri")
        
        b1 = GlossyButton("+ Node Ekle")
        b1.clicked.connect(self.open_add_node)
        p1.add_widget(b1)
        
        b2 = GlossyButton("- Node Sil")
        b2.clicked.connect(self.open_delete_node)
        p1.add_widget(b2)
        
        b3 = GlossyButton("+ Edge Ekle")
        b3.clicked.connect(self.open_add_edge)
        p1.add_widget(b3)
        
        b4 = GlossyButton("- Edge Sil")
        b4.clicked.connect(self.open_delete_edge)
        p1.add_widget(b4)
        
        l.addWidget(p1)
        
        # 2. Veri Aktarımı
        p2 = Panel("Veri Aktarımı")
        b_save = GlossyButton("💾 Kaydet (JSON)")
        b_save.clicked.connect(self.save_graph)
        p2.add_widget(b_save)

        b_revert = GlossyButton("<< Geri Al (Son Kayıt)")
        b_revert.clicked.connect(self.revert_graph)
        p2.add_widget(b_revert)
        
        b_load = GlossyButton("📂 Yükle (CSV)")
        b_load.clicked.connect(self.load_csv_dialog)
        p2.add_widget(b_load)

        b_export_mat = GlossyButton("📤 Matris Çıktısı (CSV)")
        b_export_mat.clicked.connect(self.export_matrix_dialog)
        p2.add_widget(b_export_mat)
        
        l.addWidget(p2)
        
        # 3. Algoritmalar
        p3 = Panel("Algoritmalar")
        
        b_algo1 = GlossyButton("BFS / DFS")
        b_algo1.clicked.connect(lambda: self.run_algo_dialog("bfs_dfs"))
        p3.add_widget(b_algo1)
        
        b_algo2 = GlossyButton("En Kısa Yol")
        b_algo2.clicked.connect(self.open_dijkstra)
        p3.add_widget(b_algo2)
        
        b_algo3 = GlossyButton("Topluluk Analizi")
        b_algo3.clicked.connect(self.show_components)
        p3.add_widget(b_algo3)
        
        b_algo4 = GlossyButton("Merkezilik Analizi")
        b_algo4.clicked.connect(self.show_top5)
        p3.add_widget(b_algo4)
        
        l.addWidget(p3)
        
        l.addStretch()
        parent_layout.addWidget(container)

    def create_center_col(self, parent_layout):
        container = QWidget()
        l = QVBoxLayout(container)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(10)
        
        # TOP: Graph Canvas
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor(COLORS["background"])))
        self.scene.selectionChanged.connect(self.on_selection_changed)
        # Graphics View
        self.view = ZoomableGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setStyleSheet(f"background-color: {COLORS['background']}; border: none; border-radius: 8px;")
        l.addWidget(self.view, stretch=2)
        
        # BOTTOM: Controls (Results | Settings | Coloring)
        bottom_container = QWidget()
        bottom_container.setFixedHeight(280)
        bl = QHBoxLayout(bottom_container)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(10)
        
        # P1: Sonuçlar (Table)
        self.panel_results = Panel("Sonuçlar")
        self.res_table = QTableWidget(5, 2)
        self.res_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.res_table.horizontalHeader().setStretchLastSection(True)
        self.res_table.horizontalHeader().setVisible(False) # Clean look
        self.res_table.setStyleSheet(TABLE_STYLE)
        self.panel_results.add_widget(self.res_table)
        bl.addWidget(self.panel_results, stretch=1)
        
        # P2: Algoritma Ayarları (Inputs)
        self.panel_settings = Panel("Algoritma Ayarları")
        
        # 1. Row: Algoritma Seçimi
        self.panel_settings.add_widget(QLabel("Algoritma:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["Dijkstra", "A*", "BFS", "DFS"])
        self.algo_combo.setStyleSheet(INPUT_STYLE)
        self.panel_settings.add_widget(self.algo_combo)

        # 2. Row: Başlangıç Node
        self.panel_settings.add_widget(QLabel("Başlangıç ID:"))
        self.inp_start = QLineEdit()
        self.inp_start.setPlaceholderText("Seçili veya ID (Örn: 1)")
        self.inp_start.setStyleSheet(INPUT_STYLE)
        self.panel_settings.add_widget(self.inp_start)

        # 3. Row: Hedef Node
        self.inp_target = QLineEdit()
        self.inp_target.setPlaceholderText("Node ID (Örn: 5)")
        self.inp_target.setStyleSheet(INPUT_STYLE)
        self.panel_settings.add_widget(QLabel("Hedef:"))
        self.panel_settings.add_widget(self.inp_target)

        # 4. Row: Çalıştır Butonu
        self.btn_run_algo = GlossyButton("🚀 Çalıştır")
        self.btn_run_algo.clicked.connect(self.run_algorithm_settings)
        self.panel_settings.add_widget(self.btn_run_algo)
        
        bl.addWidget(self.panel_settings, stretch=1)
        
        # P3: Graf Renklendirme
        self.panel_color = Panel("Graf Renklendirme")
        self.panel_color.add_widget(QLabel("Topluluk Tespiti ve Renklendirme"))
        
        # Color dots (Mock)
        dots = QLabel("🔴 🔵 🟢 🟡")
        dots.setAlignment(Qt.AlignCenter)
        dots.setStyleSheet("font-size: 20px; padding: 10px;")
        self.panel_color.add_widget(dots)
        
        btn_clr = GlossyButton("Renklendir")
        btn_clr.clicked.connect(self.run_coloring)
        self.panel_color.add_widget(btn_clr)
        bl.addWidget(self.panel_color, stretch=1)

        l.addWidget(bottom_container)
        parent_layout.addWidget(container, stretch=1)

    def create_right_col(self, parent_layout):
        container = QWidget()
        container.setFixedWidth(300)
        l = QVBoxLayout(container)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(10)
        
        # 1. Düğüm Bilgisi (Inspector)
        self.p_inspector = Panel("Düğüm Bilgisi")
        self.lbl_insp_id = QLabel("Seçili: Yok")
        self.lbl_insp_id.setStyleSheet(f"font-size: 14px; color: {COLORS['accent_green']}; font-weight: bold;")
        self.p_inspector.add_widget(self.lbl_insp_id)
        
        # Inputs for editing
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("Kullanıcı Adı")
        self.edit_name.setStyleSheet(INPUT_STYLE)
        self.p_inspector.add_widget(QLabel("Adı:"))
        self.p_inspector.add_widget(self.edit_name)
        
        self.edit_act = QLineEdit()
        self.edit_act.setPlaceholderText("Aktiflik (0-1)")
        self.edit_act.setStyleSheet(INPUT_STYLE)
        self.p_inspector.add_widget(QLabel("Aktiflik:"))
        self.p_inspector.add_widget(self.edit_act)
        
        self.edit_int = QLineEdit()
        self.edit_int.setPlaceholderText("Etkileşim")
        self.edit_int.setStyleSheet(INPUT_STYLE)
        self.p_inspector.add_widget(QLabel("Etkileşim:"))
        self.p_inspector.add_widget(self.edit_int)
        
        btn_save = QPushButton("Güncelle")
        btn_save.setStyleSheet(f"background-color: {COLORS['accent_blue']}; color: white; border-radius: 4px; padding: 6px;")
        btn_save.clicked.connect(self.save_node_edit)
        self.p_inspector.layout_main.addWidget(btn_save)

        l.addWidget(self.p_inspector)
        
        # 2. İstatistikler (Real Data)
        self.p_stats = Panel("İstatistikler")
        
        self.lbl_stat_nodes = QLabel("Toplam Node: 0")
        self.lbl_stat_edges = QLabel("Toplam Edge: 0")
        self.lbl_stat_density = QLabel("Yoğunluk: 0.00")
        
        # Style them
        for lbl in [self.lbl_stat_nodes, self.lbl_stat_edges, self.lbl_stat_density]:
            lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px; margin-left: 5px;")
            self.p_stats.add_widget(lbl)
            
        l.addWidget(self.p_stats)
        
        # 3. Performans
        p_perf = Panel("Performans")
        self.lbl_perf_time = QLabel("Çalışma Süresi: -")
        p_perf.add_widget(self.lbl_perf_time)
        # self.lbl_perf_mem = QLabel("Bellek Kullanımı: -") 
        # p_perf.add_widget(self.lbl_perf_mem) # Memory is harder to track precisely in Python in realtime without overhead
        l.addWidget(p_perf)
        
        l.addStretch()
        parent_layout.addWidget(container)

    # =========================
    # LOGIC
    # =========================
    def update_stats(self):
        n = len(self.graph.nodes)
        m = len(self.graph.edges)
        
        self.lbl_stat_nodes.setText(f"Toplam Node: {n}")
        self.lbl_stat_edges.setText(f"Toplam Edge: {m}")
        
        # Density for undirected graph: 2*m / (n*(n-1))
        density = 0
        if n > 1:
            density = (2 * m) / (n * (n - 1))
        
        self.lbl_stat_density.setText(f"Yoğunluk: {density:.4f}")

    def draw_graph(self):
        self.scene.clear()
        self.update_stats()
        
        nodes = self.graph.nodes
        n = len(nodes)
        
        # Determine colors
        colors = {}
        if self.is_colored:
            try:
                colors = self.graph.welsh_powell()
            except:
                colors = {}
        
        palette = ["#ef476f", "#ffd166", "#06d6a0", "#118ab2", "#073b4c"]
        default_color = "#0ea5e9" # Accent Blue for uncolored state

        # SPRING LAYOUT (Improved)
        if n == 0: return

        # Calculate layout using backend
        layout_positions = self.graph.spring_layout(width=2000, height=2000, iterations=80)
        # Assuming scene needs to be adjusted or we center it? 
        # The graph returns coordinates in range (0,0) to (2000,2000).
        # MainWindow view is likely smaller, but QGraphicsView supports scrolling/zoom.
        # Let's map them somewhat centrally initially.
        
        positions = {}
        for nid, (lx, ly) in layout_positions.items():
             positions[nid] = QPointF(lx, ly)

        # Edges
        for e in self.graph.edges:
            if e.source in positions and e.target in positions:
                self.scene.addItem(EdgeItem(e, positions[e.source], positions[e.target]))
                
        # Nodes
        for node in nodes:
            if node.id in positions:
                if self.is_colored:
                    c = palette[colors.get(node.id, 0) % len(palette)]
                else:
                    c = default_color
                self.scene.addItem(NodeItem(node, positions[node.id].x(), positions[node.id].y(), color=c))

        # Auto fit to view
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def on_selection_changed(self):
        items = self.scene.selectedItems()
        if not items:
            self.lbl_insp_id.setText("Seçili: Yok")
            self.current_node_id = None
            return
        
        for item in items:
            if isinstance(item, NodeItem):
                n = item.node
                self.current_node_id = n.id
                self.lbl_insp_id.setText(f"Kullanıcı ID: {n.id}")
                self.edit_name.setText(n.name)
                self.edit_act.setText(str(n.aktiflik))
                self.edit_int.setText(str(n.etkilesim))
                break

    def save_node_edit(self):
        if not hasattr(self, 'current_node_id') or self.current_node_id is None:
            return
        
        try:
            nid = self.current_node_id
            name = self.edit_name.text()
            act = float(self.edit_act.text())
            inter = int(self.edit_int.text())
            
            self.graph.update_node(nid, name=name, aktiflik=act, etkilesim=inter)
            self.draw_graph()
            
            # Re-select to keep focus
            for item in self.scene.items():
                if isinstance(item, NodeItem) and item.node.id == nid:
                    item.setSelected(True)
                    break

            QMessageBox.information(self, "Başarılı", "Güncellendi")
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

    # --- Actions ---
    # Need to reimplement or copy Dialogs?
    # I will create simple input dialogs for brevity to avoid file bloat, or we assume they exist.
    # To Ensure functionality, I'll add minimal dialogs inline here (same as before).
    
    def run_algo_dialog(self, type):
        dlg = TraverseDialog(self.graph)
        if dlg.exec_():
            sid, algo = dlg.get_data()
            if sid is not None:
                self.display_algorithm_results(algo, sid)
            
            
        
    def show_top5(self):
        res = self.graph.degree_centrality_top5()
        self.res_table.setRowCount(len(res))
        for i, (nid, d) in enumerate(res):
            self.res_table.setItem(i, 0, QTableWidgetItem(str(nid)))
            self.res_table.setItem(i, 1, QTableWidgetItem(str(d)))
            
    def run_coloring(self):
        self.draw_graph()

    def run_algorithm_settings(self):
        try:
            # 1. Get Start Node
            # Priority: Input Field > Selected Node
            start_id = None
            inp_sid_str = self.inp_start.text().strip()
            if inp_sid_str.isdigit():
                start_id = int(inp_sid_str)
            elif hasattr(self, 'current_node_id') and self.current_node_id is not None:
                start_id = self.current_node_id
            
            if start_id is None:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir başlangıç düğümü seçin veya ID girin.")
                return

            algo_type = self.algo_combo.currentText()
            
            # 2. Get Target for Pathfinding
            target_str = self.inp_target.text().strip()
            target_id = int(target_str) if target_str.isdigit() else None
            
            self.display_algorithm_results(algo_type, start_id, target_id)
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

    def display_algorithm_results(self, algo_type, start_id, target_id=None):
        import time
        t_start = time.perf_counter()
        
        try:
            result_msg = ""
            results_for_table = [] # List of (Key, Value) tuples
            
            if algo_type in ["Dijkstra", "A*"]:
                if target_id is None:
                    QMessageBox.warning(self, "Uyarı", f"{algo_type} için Hedef Node ID giriniz.")
                    return
                
                if algo_type == "Dijkstra":
                    path, cost = self.graph.dijkstra(start_id, target_id)
                    title = "Dijkstra"
                else: # A*
                    path, cost = self.graph.astar(start_id, target_id)
                    title = "A*"
                
                result_msg = f"{title} Sonuç:\nYol: {path}\nMaliyet: {cost:.2f}"
                
                # Prepare Table Data
                results_for_table.append(("Algoritma", title))
                results_for_table.append(("Maliyet", f"{cost:.2f}"))
                results_for_table.append(("Adım Sayısı", str(len(path))))
                for i, node_id in enumerate(path):
                    results_for_table.append((f"Adım {i+1}", f"Node {node_id}"))
                    
            elif algo_type in ["BFS", "DFS"]:
                if algo_type == "BFS":
                    res = self.graph.bfs(start_id)
                else:
                    res = self.graph.dfs(start_id)
                
                result_msg = f"{algo_type} Ziyaret Sırası:\n{res}"
                
                # Prepare Table Data
                results_for_table.append(("Algoritma", algo_type))
                results_for_table.append(("Toplam Node", str(len(res))))
                for i, node_id in enumerate(res):
                    results_for_table.append((f"{i+1}. Sıra", f"Node {node_id}"))

            # Update Table
            self.res_table.setRowCount(len(results_for_table))
            for i, (key, val) in enumerate(results_for_table):
                self.res_table.setItem(i, 0, QTableWidgetItem(str(key)))
                self.res_table.setItem(i, 1, QTableWidgetItem(str(val)))

            # Timing end
            t_end = time.perf_counter()
            duration_ms = (t_end - t_start) * 1000.0
            self.lbl_perf_time.setText(f"Çalışma Süresi: {duration_ms:.4f} ms")

            # Optional: Show popup? User asked for table, maybe popup is annoying if repeated.
            # Keeping popup for now as it's explicit feedback.
            QMessageBox.information(self, "Sonuç", result_msg)
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))


        
    def save_graph(self):
        self.graph.save_to_json(self.graph.data_path)
        QMessageBox.information(self, "Kayıt", "Kaydedildi.")

    def revert_graph(self):
        try:
            if not os.path.exists(self.graph.data_path):
                QMessageBox.warning(self, "Hata", "Kayıtlı dosya bulunamadı.")
                return
            
            self.graph.load_from_json(self.graph.data_path)
            self.is_colored = False
            self.draw_graph()
            QMessageBox.information(self, "Başarılı", "Son kaydedilen duruma geri dönüldü.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

    def load_csv_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "CSV Yükle", "", "CSV Files (*.csv)")
        if path:
            try:
                self.graph.load_from_csv(path)
                self.is_colored = False # Reset coloring on new load
                self.draw_graph()
                QMessageBox.information(self, "Başarılı", "Graf CSV'den yüklendi.")
            except Exception as e:
                QMessageBox.warning(self, "Hata", str(e))

    def export_matrix_dialog(self):
        path, _ = QFileDialog.getSaveFileName(self, "Matris Kaydet", "adjacency_matrix.csv", "CSV Files (*.csv)")
        if path:
            try:
                self.graph.export_adjacency_matrix(path)
                QMessageBox.information(self, "Başarılı", "Komşuluk matrisi kaydedildi.")
            except Exception as e:
                QMessageBox.warning(self, "Hata", str(e))

    # Minimal Dialog wrappers so buttons work
    def open_add_node(self):
        if AddNodeDialog(self.graph).exec_(): self.draw_graph()
    def open_delete_node(self):
        if DeleteNodeDialog(self.graph).exec_(): self.draw_graph()
    def open_add_edge(self):
        if AddEdgeDialog(self.graph).exec_(): self.draw_graph()
    def open_delete_edge(self):
        if DeleteEdgeDialog(self.graph).exec_(): self.draw_graph()
    def open_dijkstra(self):
         DijkstraDialog(self.graph).exec_()
    def show_components(self):
        comps = self.graph.connected_components()
        self.res_table.setRowCount(len(comps))
        for i, c in enumerate(comps):
             self.res_table.setItem(i, 0, QTableWidgetItem(f"Grup {i+1}"))
             self.res_table.setItem(i, 1, QTableWidgetItem(str(c)))

    def run_coloring(self):
        try:
            colors = self.graph.welsh_powell()
            if not colors:
                QMessageBox.information(self, "Bilgi", "Renklendirilecek düğüm yok.")
                return

            # Enable coloring mode
            self.is_colored = True

            # Chromatic number is max color index + 1 (since 0-indexed)
            chromatic_number = max(colors.values()) + 1
            
            # Palette used in draw_graph for reference
            palette_names = ["Kırmızı", "Sarı", "Yeşil", "Mavi", "Koyu Lacivert"]

            # Update Table
            # Rows: Algo Name, Chromatic Num, Header, [Node...Color]
            total_rows = 2 + 1 + len(colors) 
            self.res_table.setRowCount(total_rows)
            
            # Summary
            self.res_table.setItem(0, 0, QTableWidgetItem("Algoritma"))
            self.res_table.setItem(0, 1, QTableWidgetItem("Welsh-Powell"))
            
            self.res_table.setItem(1, 0, QTableWidgetItem("Kromatik Sayı"))
            self.res_table.setItem(1, 1, QTableWidgetItem(str(chromatic_number)))
            
            # Separator / Header
            header_item = QTableWidgetItem("--- Detaylar ---")
            header_item.setBackground(QColor(COLORS['panel']))
            header_item.setForeground(QColor(COLORS['accent_cyan']))
            self.res_table.setItem(2, 0, header_item)
            self.res_table.setItem(2, 1, QTableWidgetItem(""))

            # Node Details
            # Sort by color then ID for nicer list
            sorted_items = sorted(colors.items(), key=lambda x: (x[1], x[0]))
            
            for i, (nid, c_idx) in enumerate(sorted_items):
                row = 3 + i
                color_name = palette_names[c_idx % len(palette_names)]
                self.res_table.setItem(row, 0, QTableWidgetItem(f"Node {nid}"))
                self.res_table.setItem(row, 1, QTableWidgetItem(f"{color_name} (Kod: {c_idx})"))
            
            # Re-draw to ensure colors are applied
            self.draw_graph()
            
            QMessageBox.information(self, "Başarılı", f"Graf renklendirildi.\nKromatik Sayı: {chromatic_number}\nDetaylar tabloda listelendi.")
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

# --- DIALOG CLASSES (Simplified for file size) ---
class BaseDialog(QDialog):
    def __init__(self): 
        super().__init__()
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["panel"]}; border: 1px solid {COLORS["border"]}; }}
            QLabel {{ color: {COLORS["text"]}; font-size: 13px; font-weight: bold; margin-bottom: 2px; }}
            QLineEdit {{ 
                background-color: {COLORS["input_bg"]}; 
                border: 1px solid {COLORS["border"]}; 
                border-radius: 4px; 
                color: {COLORS["text"]}; 
                padding: 6px; 
                min-height: 20px;
            }}
            QLineEdit:focus {{ border: 1px solid {COLORS["accent_cyan"]}; }}
            QPushButton {{ 
                background-color: {COLORS["accent_blue"]}; 
                color: {COLORS["background"]}; 
                border-radius: 4px; 
                padding: 8px; 
                font-weight: bold;
                margin-top: 10px;
            }}
            QPushButton:hover {{ background-color: {COLORS["accent_cyan"]}; }}
            QComboBox {{
                background-color: {COLORS["input_bg"]};
                border: 1px solid {COLORS["border"]};
                color: {COLORS["text"]};
                padding: 5px;
            }}
        """) 
class AddNodeDialog(BaseDialog):
    def __init__(self, g):
        super().__init__();
        self.g=g; self.setWindowTitle("Ekle")
        l=QVBoxLayout(self); 
        self.inputs=[QLineEdit() for _ in range(4)]
        labels=["ID","Ad","Aktiflik","Etkileşim"]
        for i,lb in enumerate(labels): l.addWidget(QLabel(lb)); l.addWidget(self.inputs[i])
        b=QPushButton("Ekle"); b.clicked.connect(self.act); l.addWidget(b)
    def act(self):
        try: 
            self.g.add_node(Node(int(self.inputs[0].text()), self.inputs[1].text(), float(self.inputs[2].text()), int(self.inputs[3].text())))
            self.accept()
        except Exception as e: QMessageBox.warning(self,"Hata",str(e))

class DeleteNodeDialog(BaseDialog):
    def __init__(self, g):
        super().__init__(); self.g=g; self.setWindowTitle("Sil"); l=QVBoxLayout(self)
        self.i=QLineEdit(); l.addWidget(QLabel("ID")); l.addWidget(self.i); 
        b=QPushButton("Sil"); b.clicked.connect(lambda: (self.g.remove_node(int(self.i.text())), self.accept())); l.addWidget(b)

class AddEdgeDialog(BaseDialog):
    def __init__(self, g):
        super().__init__(); self.g=g; self.setWindowTitle("Edge Ekle"); l=QVBoxLayout(self)
        self.i1=QLineEdit(); self.i2=QLineEdit(); l.addWidget(self.i1); l.addWidget(self.i2)
        b=QPushButton("Ekle"); b.clicked.connect(lambda: (self.g.add_edge(int(self.i1.text()), int(self.i2.text())), self.accept())); l.addWidget(b)

class DeleteEdgeDialog(BaseDialog):
    def __init__(self, g):
        super().__init__(); self.g=g; self.setWindowTitle("Edge Sil"); l=QVBoxLayout(self)
        self.i1=QLineEdit(); self.i2=QLineEdit(); l.addWidget(self.i1); l.addWidget(self.i2)
        b=QPushButton("Sil"); b.clicked.connect(lambda: (self.g.remove_edge(int(self.i1.text()), int(self.i2.text())), self.accept())); l.addWidget(b)

class DijkstraDialog(BaseDialog):
    def __init__(self, g):
        super().__init__(); self.g=g; self.setWindowTitle("Dijkstra"); l=QVBoxLayout(self)
        self.i1=QLineEdit(); self.i2=QLineEdit(); l.addWidget(QLabel("Başlangıç ID")); l.addWidget(self.i1); l.addWidget(QLabel("Bitiş ID")); l.addWidget(self.i2)
        b=QPushButton("Hesapla"); b.clicked.connect(self.act); l.addWidget(b)
    def act(self):
        try:
             p,c = self.g.dijkstra(int(self.i1.text()), int(self.i2.text()))
             QMessageBox.information(self,"Sonuç",f"Yol: {p}\nMaliyet: {c}")
        except Exception as e: QMessageBox.warning(self,"Hata",str(e))

class TraverseDialog(BaseDialog):
    def __init__(self, g):
        super().__init__()
        self.g = g
        self.setWindowTitle("BFS / DFS")
        self.layout_main = QVBoxLayout(self)
        
        self.layout_main.addWidget(QLabel("Başlangıç Node ID:"))
        self.inp_start = QLineEdit()
        self.inp_start.setPlaceholderText("ID giriniz (örn: 1)")
        self.inp_start.setStyleSheet(INPUT_STYLE)
        self.layout_main.addWidget(self.inp_start)
        
        self.layout_main.addWidget(QLabel("Algoritma:"))
        self.cb_algo = QComboBox()
        self.cb_algo.addItems(["BFS", "DFS"])
        self.cb_algo.setStyleSheet(INPUT_STYLE)
        self.layout_main.addWidget(self.cb_algo)
        
        btn = QPushButton("Çalıştır")
        btn.setStyleSheet(BUTTON_STYLE)
        btn.clicked.connect(self.run_algo)
        self.layout_main.addWidget(btn)
        
        self.data_out = (None, None)
        
    def run_algo(self):
        try:
            sid = int(self.inp_start.text())
            algo = self.cb_algo.currentText()
            self.data_out = (sid, algo)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))
            
    def get_data(self):
        return self.data_out


class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        # Enable Scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self._panning = False
        self._pan_start = QPointF(0, 0)

    def mousePressEvent(self, event):
        # Allow Right Click OR Middle Click for panning
        if event.button() == Qt.RightButton or event.button() == Qt.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton or event.button() == Qt.MiddleButton:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Save the scene pos
        old_pos = self.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        
        self.scale(zoom_factor, zoom_factor)

        # Get the new position
        new_pos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(MAIN_APP_STYLE) # Apply style globally to fix dialogs/modals
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
