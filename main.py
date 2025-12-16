import os
print("CALISAN DOSYA:", os.path.abspath(__file__))
print(">>> GUNCEL MAIN.PY CALISIYOR <<<")

import tkinter as tk
from tkinter import messagebox

from ui.src.graph import Graph
from ui.src.node import Node

# =========================
# GRAPH NESNESİ
# =========================
graph = Graph()

# =========================
# ANA PENCERE
# =========================
root = tk.Tk()
root.title("Sosyal Ağ Analizi Uygulaması")
root.geometry("1000x600")

# =========================
# NODE EKLE POPUP (SON & NET)
# =========================
def open_add_node_popup():
    print("NODE POPUP ACILDI")

    popup = tk.Toplevel(root)
    popup.title("Node Ekle")
    popup.geometry("400x420")
    popup.minsize(400, 420)
    popup.grab_set()
    popup.configure(bg="#f2f2f2")

    # ---- INPUTLAR ----
    tk.Label(popup, text="Node ID", bg="#f2f2f2").pack(anchor="w", padx=20, pady=(20, 0))
    entry_id = tk.Entry(popup, width=35)
    entry_id.pack(padx=20, pady=5)

    tk.Label(popup, text="İsim", bg="#f2f2f2").pack(anchor="w", padx=20, pady=(10, 0))
    entry_name = tk.Entry(popup, width=35)
    entry_name.pack(padx=20, pady=5)

    tk.Label(popup, text="Aktiflik (0-1)", bg="#f2f2f2").pack(anchor="w", padx=20, pady=(10, 0))
    entry_aktiflik = tk.Entry(popup, width=35)
    entry_aktiflik.pack(padx=20, pady=5)

    tk.Label(popup, text="Etkileşim", bg="#f2f2f2").pack(anchor="w", padx=20, pady=(10, 0))
    entry_etkilesim = tk.Entry(popup, width=35)
    entry_etkilesim.pack(padx=20, pady=5)

    # ---- NODE EKLE AKSİYONU ----
    def add_node_action():
        try:
            if not all([
                entry_id.get().strip(),
                entry_name.get().strip(),
                entry_aktiflik.get().strip(),
                entry_etkilesim.get().strip()
            ]):
                raise ValueError("Tüm alanlar doldurulmalıdır.")

            node_id = int(entry_id.get())
            aktiflik = float(entry_aktiflik.get())
            etkilesim = int(entry_etkilesim.get())

            if not (0 <= aktiflik <= 1):
                raise ValueError("Aktiflik 0 ile 1 arasında olmalı.")

            node = Node(
                node_id,
                entry_name.get(),
                aktiflik,
                etkilesim,
                0,
                []
            )

            graph.add_node(node)
            messagebox.showinfo("Başarılı", "Node başarıyla eklendi.")
            popup.destroy()

        except Exception as e:
            messagebox.showerror("Hata", str(e))

    tk.Button(popup, text="Ekle", command=add_node_action).pack(pady=25)

# =========================
# SOL PANEL (KONTROLLER)
# =========================
left_frame = tk.Frame(root, width=250, bg="#f0f0f0")
left_frame.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(
    left_frame,
    text="Kontrol Paneli",
    font=("Arial", 14, "bold"),
    bg="#f0f0f0"
).pack(pady=10)

tk.Button(
    left_frame,
    text="Node Ekle",
    command=open_add_node_popup
).pack(fill=tk.X, padx=10, pady=5)

tk.Button(left_frame, text="Edge Ekle").pack(fill=tk.X, padx=10, pady=5)
tk.Button(left_frame, text="BFS Çalıştır").pack(fill=tk.X, padx=10, pady=5)
tk.Button(left_frame, text="DFS Çalıştır").pack(fill=tk.X, padx=10, pady=5)

tk.Button(
    left_frame,
    text="JSON Kaydet",
    command=lambda: graph.save_to_json("data/graph.json")
).pack(fill=tk.X, padx=10, pady=20)

# =========================
# SAĞ PANEL (CANVAS)
# =========================
right_frame = tk.Frame(root, bg="white")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

tk.Label(
    right_frame,
    text="Graf Çizim Alanı (Canvas)",
    font=("Arial", 12),
    bg="white"
).pack(pady=5)

tk.Canvas(
    right_frame,
    bg="white"
).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# =========================
# PROGRAMI BAŞLAT
# =========================
root.mainloop()
