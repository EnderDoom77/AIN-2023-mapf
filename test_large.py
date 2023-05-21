import random
from graph import Graph


n = 100
edges = 250

g = Graph(n)
rng = random.Random()

print("Adding edges")
for i in range(edges):
    a = rng.randint(0, n-1)
    b = rng.randint(0, n-1)
    g.add_edge(a,b)

print("Finished adding edges")
g.visualize(show_distances=False)
print("Visualization successful")