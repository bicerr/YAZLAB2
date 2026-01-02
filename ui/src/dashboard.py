
import math

from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout,
    QPushButton
)
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont, QPen, QLinearGradient
from PyQt5.QtCore import Qt, QSize

from ui.src.styles import COLORS, PANEL_STYLE, TABLE_STYLE


class MetricCard(QFrame):
    def __init__(self, title, value, subtext="", color=COLORS["accent_blue"]):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['panel']};
                border: 1px solid {COLORS['glass_border']};
                border-radius: 8px;
            }}
        """)
        self.layout_main = QVBoxLayout(self)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #64748b; font-size: 13px; font-weight: bold; border: none;")
        self.layout_main.addWidget(lbl_title)
        
        lbl_val = QLabel(str(value))
        lbl_val.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold; border: none;")
        self.layout_main.addWidget(lbl_val)
        
        if subtext:
             lbl_sub = QLabel(subtext)
             lbl_sub.setStyleSheet("color: #94a3b8; font-size: 11px; border: none;")
             self.layout_main.addWidget(lbl_sub)
             
class SimpleBarChart(QWidget):
    def __init__(self, data, color=COLORS["accent_blue"]):
        """
        data: list of tuples (label, value)
        """
        super().__init__()
        self.data = data
        self.bar_color = QColor(color)
        self.setMinimumHeight(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        if not self.data:
            painter.setPen(Qt.white)
            painter.drawText(self.rect(), Qt.AlignCenter, "Veri Yok")
            return

        max_val = max([x[1] for x in self.data]) if self.data else 1
        if max_val == 0: max_val = 1
        
        bar_width = w / (len(self.data) * 1.5)
        spacing = bar_width / 2.0
        
        current_x = spacing
        
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        for label, val in self.data:
            bar_h = (val / max_val) * (h - 40)
            
            real_h = int(bar_h) if int(bar_h) > 0 else 1
            rect_x = int(current_x)
            rect_y = int(h - 20 - bar_h)
            
            gradient = QLinearGradient(0, rect_y, 0, rect_y + real_h)
            gradient.setColorAt(0, self.bar_color.lighter(130)) # Lighter top
            gradient.setColorAt(1, self.bar_color.darker(110))  # Darker bottom
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            
            
            
            painter.drawRoundedRect(int(rect_x), int(rect_y), int(bar_width), int(bar_h), 4, 4)
            
            painter.setPen(QPen(QColor(COLORS["text_muted"])))
            
            
            painter.drawText(int(rect_x), int(h - 18), int(bar_width), 15, Qt.AlignCenter, str(label))
            
            painter.setPen(QPen(Qt.white))
            painter.drawText(int(rect_x), int(rect_y - 18), int(bar_width), 15, Qt.AlignCenter, str(val))
            
            current_x += bar_width + spacing

class SimpleGauge(QWidget):
    def __init__(self, value, max_value=1.0, title=""):
        super().__init__()
        self.value = value
        self.max_value = max_value if max_value > 0 else 1
        self.title = title
        self.setMinimumHeight(150)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        size = min(w, h) - 40
        x = (w - size) / 2
        y = (h - size) / 2 + 10
        
        pen_bg = QPen(QColor("#1e293b"), 12, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(int(x), int(y), int(size), int(size), 180 * 16, -180 * 16)
        
        ratio = self.value / self.max_value
        span = int(-180 * ratio * 16)
        
        pen_val = QPen(QColor(COLORS["accent_green"]), 12, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen_val)
        painter.drawArc(int(x), int(y), int(size), int(size), 180 * 16, span)
        
        painter.setPen(Qt.white)
        font = QFont("Arial", 20, QFont.Bold)
        painter.setFont(font)
        txt = f"{self.value:.2f}"
        painter.drawText(self.rect(), Qt.AlignCenter, txt)
        
        painter.setPen(QColor(COLORS["text_muted"]))
        font2 = QFont("Arial", 10)
        painter.setFont(font2)
        painter.drawText(int(x), int(y + size/2 + 20), int(size), 20, Qt.AlignCenter, self.title)

from PyQt5.QtCore import pyqtSignal

class DashboardWidget(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, graph):
        super().__init__()
        self.graph = graph
        
        layout_main = QVBoxLayout(self)
        layout_main.setContentsMargins(20, 20, 20, 20)
        layout_main.setSpacing(20)
        
        header_layout = QHBoxLayout()
        
        btn_back = QPushButton("<< Geri Dön")
        btn_back.setStyleSheet(f"background-color: {COLORS['input_bg']}; color: {COLORS['text']}; border: 1px solid {COLORS['border']}; padding: 8px 15px; border-radius: 4px;")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.emit_back)
        header_layout.addWidget(btn_back)
        
        lbl_header = QLabel("İstatistik ve Metrik Panosu")
        lbl_header.setStyleSheet(f"color: {COLORS['text']}; font-size: 22px; font-weight: bold; margin-left: 10px;")
        header_layout.addWidget(lbl_header)
        
        header_layout.addStretch()
        layout_main.addLayout(header_layout)
        
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        
        node_count = len(graph.nodes)
        edge_count = len(graph.edges)
        
        density = 0
        if node_count > 1:
            density = (2 * edge_count) / (node_count * (node_count - 1))
            
        panel_deg = QFrame()
        panel_deg.setStyleSheet(f"background-color: {COLORS['panel']}; border-radius: 8px; border: 1px solid {COLORS['glass_border']};")
        l_deg = QVBoxLayout(panel_deg)
        l_deg.addWidget(QLabel("Derece Merkeziliği (İlk 10)"))
        
        top_deg = sorted(graph.nodes, key=lambda n: n.baglanti_sayisi, reverse=True)[:10]
        data_deg = [(str(n.id), n.baglanti_sayisi) for n in top_deg]
        
        chart_deg = SimpleBarChart(data_deg, color="#3b82f6")
        l_deg.addWidget(chart_deg)
        row1.addWidget(panel_deg, stretch=2)
        
        
        panel_mid = QFrame()
        panel_mid.setStyleSheet(f"background-color: {COLORS['panel']}; border-radius: 8px; border: 1px solid {COLORS['glass_border']};")
        l_mid = QVBoxLayout(panel_mid)
        l_mid.addWidget(QLabel("Ağ Yoğunluğu (Density)"))
        
        gauge_density = SimpleGauge(density, 1.0, "Yoğunluk Skoru")
        l_mid.addWidget(gauge_density)
        row1.addWidget(panel_mid, stretch=1)
        
        panel_right = QFrame()
        panel_right.setStyleSheet(f"background-color: {COLORS['panel']}; border-radius: 8px; border: 1px solid {COLORS['glass_border']};")
        l_right = QVBoxLayout(panel_right)
        l_right.addWidget(QLabel("Genel Özet"))
        
        l_right.addWidget(MetricCard("Toplam Düğüm", node_count, "Aktör Sayısı"))
        l_right.addWidget(MetricCard("Toplam Bağlantı", edge_count, "İlişki Sayısı"))
        
        row1.addWidget(panel_right, stretch=1)
        
        layout_main.addLayout(row1, stretch=4)
        
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        
        panel_table = QFrame()
        panel_table.setStyleSheet(f"background-color: {COLORS['panel']}; border-radius: 8px; border: 1px solid {COLORS['glass_border']};")
        l_tbl = QVBoxLayout(panel_table)
        lbl_tbl = QLabel("En Etkili Aktörler Listesi")
        lbl_tbl.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        l_tbl.addWidget(lbl_tbl)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID", "İsim", "Derece", "Aktiflik"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet(TABLE_STYLE)
        
        table.setRowCount(len(top_deg))
        for i, n in enumerate(top_deg):
            table.setItem(i, 0, QTableWidgetItem(str(n.id)))
            table.setItem(i, 1, QTableWidgetItem(n.name))
            table.setItem(i, 2, QTableWidgetItem(str(n.baglanti_sayisi)))
            table.setItem(i, 3, QTableWidgetItem(str(n.aktiflik)))
            
        l_tbl.addWidget(table)
        row2.addWidget(panel_table, stretch=2)
        
        panel_closeness = QFrame()
        panel_closeness.setStyleSheet(f"background-color: {COLORS['panel']}; border-radius: 8px; border: 1px solid {COLORS['glass_border']};")
        l_close = QVBoxLayout(panel_closeness)
        l_close.addWidget(QLabel("Yakınlık Merkeziliği (İlk 5)"))
        
        data_close = []
        for n in top_deg[:5]:
            try:
                path, dists = image_dijkstra_all(graph, n.id) 
                total_dist = sum(dists.values())
                if total_dist > 0:
                    val = (node_count - 1) / total_dist
                else:
                     val = 0
                data_close.append((str(n.id), round(val, 4)))
            except:
                data_close.append((str(n.id), 0))
        
        chart_close = SimpleBarChart(data_close, color="#f59e0b")
        l_close.addWidget(chart_close)
        
        row2.addWidget(panel_closeness, stretch=1)
        
        layout_main.addLayout(row2, stretch=3)

    def emit_back(self):
        self.back_clicked.emit()

def image_dijkstra_all(graph, start_id):
    import heapq
    distances = {node.id: float("inf") for node in graph.nodes}
    distances[start_id] = 0
    pq = [(0, start_id)]
    
    while pq:
        d, u = heapq.heappop(pq)
        if d > distances[u]: continue
        
        u_node = graph.get_node_by_id(u)
        if not u_node: continue
        
        for v in u_node.komsular:
            v_node = graph.get_node_by_id(v)
            weight = graph.calculate_weight(u_node, v_node)
            cost = 1.0 / weight if weight > 0 else float('inf')
            
            if distances[u] + cost < distances[v]:
                distances[v] = distances[u] + cost
                heapq.heappush(pq, (distances[v], v))
                
    reachable = {k: v for k, v in distances.items() if v != float("inf")}
    return None, reachable
