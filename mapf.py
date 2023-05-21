from collections import defaultdict
import heapq
from typing import Dict, List, Set, Tuple
from typing_extensions import override
from graph import Graph

def build_path(camefrom: List[int|None], origin:int, goal:int):
    curr = goal
    revresult = [goal]
    while curr != origin and curr != None:
        curr = camefrom[curr]
        revresult.append(curr)
        
    if curr != origin: return None
    return list(reversed(revresult))

def a_star_coop(graph: Graph, start: int, goal: int, 
    reservations: Dict[int, Set[int]]) -> List[int] | None:
    # cost map, preloaded with infinity
    g = [float("+inf") for _ in range(graph.size)]
    g[start] = 0
    
    # traceback to build path later
    trace = [None for _ in range(graph.size)]
    
    open_list = [(graph.distance(start, goal), 0, start)]
    closed_list: Set[int] = set()
    
    while open_list != []:
        f_node, t, node = heapq.heappop(open_list)
        if node in closed_list:
            continue
        if node == goal:
            return build_path(trace, start, goal)
        closed_list.add(node)
        for adj,g_adj in graph.neighbours(node) + [(node, 0)]:
            # that tile can't be used or has been explored
            if adj in closed_list:
                continue
            # that tile can't be used if it's reserved totally or from our location
            if (adj,adj) in reservations[t+1] or (node,adj) in reservations[t+1]:
                continue
            g_new = g[node] + g_adj
            # we already found a lower-cost path to the neighbour
            if g_new >= g[adj]:
                continue
            
            f = g_new + graph.distance_heuristic(adj,goal)
            heapq.heappush(open_list, (f,t+1,adj))
            
            trace[adj] = node
            g[adj] = g_new

def multi_agent_pathfinding(graph: Graph, 
    start: List[int], goal: List[int]) -> List[List[int] | None]:
    result, reservations = multi_agent_pathfinding_with_reservations(graph, start, goal)
    return result

def multi_agent_pathfinding_with_reservations(graph: Graph, 
    start: List[int], goal: List[int]) -> Tuple[List[List[int] | None], Dict[int, Set]]:
    # Initialize the reservations table
    reservations : Dict[int,Set] = defaultdict(set)
    plans = []
    for s,g in zip(start, goal):
        plan = a_star_coop(graph, s, g, reservations)
        plans.append(plan)
        if not plan:
            continue
        for t in range(len(plan)-1):
            reservations[t].add((plan[t],plan[t]))
            if t > 0: # Reserve swaps
                reservations[t].add((plan[t],plan[t-1]))
        for t in range(len(plan)-1,graph.size):
            reservations[t].add((g,g))
    return plans, reservations