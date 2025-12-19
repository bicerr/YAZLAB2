from edge import Edge

e = Edge(1, 2, 0.85)
print(e)

print(e.matches(1, 2))  # True
print(e.matches(2, 1))  # True
print(e.matches(1, 3))  # False
