from collections import defaultdict
from typing import List, Dict, Tuple
import heapq
from typing_extensions import override
import graphviz

class Graph:
    def __init__(self, n:int):
        self._neighbours: Dict[int, List[Tuple[int,float]]] = defaultdict(list)
        self.size = n
        self._distances: Dict[int, Dict[int,float]] = {}
        self.clear_distances()
        
    def clear_distances(self):
        self._distances = defaultdict(dict)
        for node in range(self.size):
            self._distances[node][node] = 0
            
    def clear_edges(self):
        self._neighbours = defaultdict(list)
    
    def add_edge(self, origin: int, destination: int, distance = 1.0):
        self.remove_edges(origin, destination)
        
        self._neighbours[origin].append((destination, distance))
        self.clear_distances()
    
    def remove_edges(self, origin, destination):
        self._neighbours[origin] = list(filter(lambda t: t[0] != destination, self._neighbours[origin]))
    
    def add_edge_bidirectional(self, origin: int, destination: int, distance = 1.0):
        self.add_edge(origin, destination, distance)
        self.add_edge(destination, origin, distance)
        
    def neighbours(self, n:int) -> List[Tuple[int,float]]:
        return self._neighbours[n]
    
    def _calculate_distances(self, origin: int):
        self._distances[origin] = {n: float("+inf") for n in range(self.size)}
        self._distances[origin][origin] = 0

        # A queue initialized with all known distances from origin to destination
        q = [(0, origin)]
        heapq.heapify(q)
        
        while q != []:
            dist, node = heapq.heappop(q)
            
            for adj, cost in self.neighbours(node):
                new_dist = dist + cost
                # if we found a better path to that node, don't go there
                if self._distances[origin][adj] <= new_dist:
                    continue
                self._distances[origin][adj] = new_dist
                heapq.heappush(q, (new_dist, adj))
    
    def calculate_distances(self):
        for origin in range(self.size):
            self._calculate_distances(origin)
    
    def distance(self, origin: int, destination: int) -> float:
        if destination not in self._distances[origin]:
            self._calculate_distances(origin)
        return self._distances[origin][destination]
    
    def distance_heuristic(self, origin: int, destination: int) -> float:
        return self.distance(origin, destination)
    
    def visualize(self, comment="Graph", colors:List[str]=None, show_distances=True, show_isolated=True):
        print("Preprocessing...")
        dot = graphviz.Digraph(comment=comment)
        if not colors:
            colors = ["black" for _ in range(self.size)]
        
        print("Adding nodes to the graph render")
        for n in range(self.size):
            if show_isolated or self.neighbours(n) != []:
                dot.node(str(n), str(n+1), {"color":colors[n]})
        print("Adding edges to the graph render")
        for n in range(self.size):
            for adj,d in self.neighbours(n):
                dot.edge(str(n), str(adj),f"{d:.1f}" if show_distances else None)
        print("Running graphviz renderer")
        dot.render('output/graph.gv', view=True)
        
class GridGraph(Graph):
    WALL_CHAR = "#"
    
    def __init__(self, dim_x: int, dim_y: int):
        super().__init__(dim_x * dim_y)
        self.cells = [[GridGraph.WALL_CHAR for _ in range(dim_x)] for _ in range(dim_y)]
        self.dim_x = dim_x
        self.dim_y = dim_y
    
    def id_from_coords(self, x:int, y:int):
        return y * self.dim_x + x
    def coords_from_id(self, id:int):
        return (id % self.dim_x, id // self.dim_x)
    
    def load_cells(self, grid: List[str]):
        self.cells = [[GridGraph.WALL_CHAR for _ in range(self.dim_x)] for _ in range(self.dim_y)]
        self._neighbours = defaultdict(list) # Empty all data
        for y,row in enumerate(grid[:self.dim_y]):
            for x,c in enumerate(row[:self.dim_x]):
                print(c,end="")
                if c != GridGraph.WALL_CHAR:
                    self.cells[y][x] = " "
                    cell_id = self.id_from_coords(x, y)
                    if y > 0 and self.cells[y-1][x] != GridGraph.WALL_CHAR:
                        top_id = self.id_from_coords(x,y-1)
                        self.add_edge_bidirectional(cell_id, top_id)
                    if x > 0 and self.cells[y][x-1] != GridGraph.WALL_CHAR:
                        left_id = self.id_from_coords(x-1,y)
                        self.add_edge_bidirectional(cell_id, left_id)
                        
            print()
        print()
        print("v" * self.dim_x)
        print()
        print("\n".join("".join(row) for row in self.cells))
                        
    @override
    def distance_heuristic(self, origin: int, destination: int) -> float:
        x1,y1 = self.coords_from_id(origin)
        x2,y2 = self.coords_from_id(destination)
        return abs(x1-x2) + abs(y1-y2)
