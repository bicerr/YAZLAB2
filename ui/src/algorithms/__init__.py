def __init__(self, data_path=None, autosave=True):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    self.data_path = data_path or os.path.join(base_dir, "data", "graph.json")
    self.autosave = autosave
    self.nodes = []
    self.edges = []
