class Node:
    def __init__(self, node_id, name, aktiflik, etkilesim, baglanti_sayisi, komsular=None):
        self.id = node_id
        self.name = name
        self.aktiflik = aktiflik
        self.etkilesim = etkilesim
        self.baglanti_sayisi = baglanti_sayisi
        self.komsular = komsular or []
