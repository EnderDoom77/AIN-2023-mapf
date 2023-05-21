from graph import Graph

n = 5
g = Graph(n)
edges = [(1,2), (2,3), (1,0), (4,0), (2,4)]
highlight = {0, 3}

for a,b in edges:
    g.add_edge_bidirectional(a,b)

colors = ["red" if i in highlight else "black" for i in range(n)]
g.visualize(colors=colors)
