class Node:
    def __init__(
        self,
        node_id,
        name,
        aktiflik=0.0,
        etkilesim=0.0,
        baglanti_sayisi=0,
        komsular=None
    ):
        self.id = node_id
        self.name = name

        self.aktiflik = aktiflik
        self.etkilesim = etkilesim
        self.baglanti_sayisi = baglanti_sayisi

        if komsular is None:
            self.komsular = []
        else:
            self.komsular = list(komsular)

    
    def komsu_ekle(self, node_id):
        if node_id not in self.komsular:
            self.komsular.append(node_id)
            self.baglanti_sayisi = len(self.komsular)

    def komsu_sil(self, node_id):
        if node_id in self.komsular:
            self.komsular.remove(node_id)
            self.baglanti_sayisi = len(self.komsular)

    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "aktiflik": self.aktiflik,
            "etkilesim": self.etkilesim,
            "baglanti_sayisi": self.baglanti_sayisi,
            "komsular": self.komsular
        }

    @staticmethod
    def from_dict(data):
        return Node(
            node_id=data["id"],
            name=data["name"],
            aktiflik=data.get("aktiflik", 0.0),
            etkilesim=data.get("etkilesim", 0.0),
            baglanti_sayisi=data.get("baglanti_sayisi", 0),
            komsular=data.get("komsular", [])
        )

    
    def __repr__(self):
        return (
            f"Node(id={self.id}, name='{self.name}', "
            f"aktiflik={self.aktiflik}, etkilesim={self.etkilesim}, "
            f"baglanti_sayisi={self.baglanti_sayisi})"
        )
