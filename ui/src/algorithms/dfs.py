class DFS:
    @staticmethod
    def run(graph, start_id):
        visited = set()
        result = []

        def dfs_recursive(node_id):
            visited.add(node_id)
            result.append(node_id)

            node = graph.get_node_by_id(node_id)
            if node:
                for neighbor in node.komsular:
                    if neighbor not in visited:
                        dfs_recursive(neighbor)

        dfs_recursive(start_id)
        return result
