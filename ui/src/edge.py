class Edge:
    def __init__(self, source, target, weight=1.0):
        if source == target:
            raise ValueError("Self-loop (aynı node'a edge) yasaktır.")

        self.source = source
        self.target = target
        self.weight = weight

    
    def to_dict(self):
        return {
            "from": self.source,
            "to": self.target,
            "weight": self.weight
        }

    @staticmethod
    def from_dict(data):
        return Edge(
            source=data["from"],
            target=data["to"],
            weight=data.get("weight", 1.0)
        )

    
    def matches(self, u, v):
        return (
            (self.source == u and self.target == v) or
            (self.source == v and self.target == u)
        )

    def __repr__(self):
        return (
            f"Edge({self.source} <-> {self.target}, "
            f"weight={self.weight:.4f})"
        )
