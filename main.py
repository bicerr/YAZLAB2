import tkinter as tk
from tkinter import ttk

# Ana pencere
root = tk.Tk()
root.title("Sosyal Ağ Analizi Uygulaması")
root.geometry("1000x600")

# =========================
# SOL PANEL (Kontroller)
# =========================
left_frame = tk.Frame(root, width=250, bg="#f0f0f0")
left_frame.pack(side=tk.LEFT, fill=tk.Y)

title = tk.Label(
    left_frame,
    text="Kontrol Paneli",
    font=("Arial", 14, "bold"),
    bg="#f0f0f0"
)
title.pack(pady=10)

btn_add_node = tk.Button(left_frame, text="Node Ekle")
btn_add_node.pack(fill=tk.X, padx=10, pady=5)

btn_add_edge = tk.Button(left_frame, text="Edge Ekle")
btn_add_edge.pack(fill=tk.X, padx=10, pady=5)

btn_bfs = tk.Button(left_frame, text="BFS Çalıştır")
btn_bfs.pack(fill=tk.X, padx=10, pady=5)

btn_dfs = tk.Button(left_frame, text="DFS Çalıştır")
btn_dfs.pack(fill=tk.X, padx=10, pady=5)

btn_save = tk.Button(left_frame, text="JSON Kaydet")
btn_save.pack(fill=tk.X, padx=10, pady=20)

# =========================
# SAĞ PANEL (CANVAS)
# =========================
right_frame = tk.Frame(root, bg="white")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

canvas_label = tk.Label(
    right_frame,
    text="Graf Çizim Alanı (Canvas)",
    font=("Arial", 12),
    bg="white"
)
canvas_label.pack(pady=5)

canvas = tk.Canvas(
    right_frame,
    bg="white"
)
canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Programı başlat
root.mainloop()
