from collections import deque

class BFS:
    @staticmethod
    def run(graph, start_id):
        visited = set()
        queue = deque([start_id])
        result = []

        while queue:
            current = queue.popleft()

            if current not in visited:
                visited.add(current)
                result.append(current)

                node = graph.get_node_by_id(current)
                if node:
                    for neighbor in node.komsular:
                        if neighbor not in visited:
                            queue.append(neighbor)

        return result
