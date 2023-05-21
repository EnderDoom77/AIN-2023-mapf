from collections import defaultdict
from typing import Dict, Generator, List, Set, Tuple
from agent import Agent
from graph import Graph, GridGraph

import argparse
import pygame

from mapf import a_star_coop, multi_agent_pathfinding, multi_agent_pathfinding_with_reservations

def read_grid(filename: str) -> Tuple[GridGraph, Dict[str, Agent]]:
    grid : List[str] = []
    with open(filename, 'r') as f:
        for line in f:
            grid.append(line.strip())
    
    graph = GridGraph(max(len(row) for row in grid), len(grid))
    graph.load_cells(grid)
    agents: Dict[str, Agent] = dict()
    for y,row in enumerate(grid):
        for x,c in enumerate(row):
            if c in ["#", " "]: continue
            c_low = c.lower()
            c_upp = c.upper()
            if c_low == c_upp: continue
            if c_low not in agents:
                agents[c_low] = Agent(c_low, -1, -1)
            if c == c_low:
                agents[c_low].init_pos = graph.id_from_coords(x,y)
            else:
                agents[c_low].goal = graph.id_from_coords(x,y)
    return (graph, agents)

def generate_colors(n: int, s: float = 100, v: float = 100, a: float = 100) -> Generator[pygame.Color, any, any]:
    hdelta = 360 / n
    for i in range(n):
        color = pygame.Color(0,0,0)
        color.hsva = (hdelta * i, s, v, a)
        yield color
        
def to_html_color(color: pygame.color.Color):
    value = (color.r << 16) + (color.g << 8) + color.b
    return f"#{value:x}"

def run_mapf(graph: Graph, agents: List[Agent]) -> Dict[int, Set[int]]:
    start = [a.init_pos for a in agents]
    goal = [a.goal for a in agents]
    positions, res = multi_agent_pathfinding_with_reservations(graph, start, goal)
    for i,path in enumerate(positions):
        if path == None:
            agents[i].coop_path = [-1]
        else:
            agents[i].coop_path = path
    return res

def run_astar(graph: Graph, agents: List[Agent]):
    for a in agents:
        path = a_star_coop(graph, a.init_pos, a.goal, defaultdict(set))
        if path == None:
            a.optimal_path = [-1]
        else:
            a.optimal_path = path

COOP_MODE = 1
INDEP_MODE = 2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default = "grid.txt", type=str, dest="file",
        help="use a specific file to initialize the grid")
    parser.add_argument("-r", "--reservations", action="store_true", dest="reservations",
        help="visualize reservation at any given time step as grey squares")
    parser.add_argument("-g", "--graph", action="store_true", dest="graph",
        help="open a pdf viewer of the graph that represents the desired grid")
    parser.add_argument("-W", "--width", type=int, default=1280, dest="display_width",
        help="sets the maximum display width")
    parser.add_argument("-H", "--height", type=int, default=720, dest="display_height",
        help="sets the maximum display height")
    args = parser.parse_args()
    
    filename = args.file
    SHOW_RESERVATIONS = args.reservations
    SHOW_GRAPH = args.graph
    SHOW_PATHS = False
    
    graph, agents = read_grid(filename)
    agents = {a: agents[a] for a in sorted(agents.keys())}
    agent_colors: Dict[str, pygame.Color] = {}
    _colorlist = list(generate_colors(len(agents),s=80,v=80))
    agent_offsets: Dict[str, float] = {a.name: 0.3 + i * 0.4 / (len(agents) - 1) for i,a in enumerate(agents.values())}
    for a, c in zip(agents.keys(), _colorlist):
        agent_colors[a] = c
    
    DISPLAY_WIDTH = args.display_width
    DISPLAY_HEIGHT = args.display_height
    
    res = run_mapf(graph, list(agents.values()))
    run_astar(graph, list(agents.values()))
    
    move_mode = COOP_MODE
    for a, agent in agents.items():
        agent.positions = agent.coop_path
    
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    agent_time = 0
    
    TILE_SIZE = min(DISPLAY_WIDTH // graph.dim_x, DISPLAY_HEIGHT // graph.dim_y)
    screen = pygame.display.set_mode((TILE_SIZE * graph.dim_x, TILE_SIZE * graph.dim_y))
    font = pygame.font.SysFont(None, int(TILE_SIZE * 0.6))
    
    # graph.visualize(show_distances=False)
    
    controls_render = font.render(f"[Left]/[A] : Back | [Right]/[D] : Forward | [0]: Start | [9]: End | [M] : Toggle Move Mode | [P] : Toggle Path Display", True, (255,255,255))
    
    if SHOW_GRAPH:
        colors = ["black" for _ in range(graph.size)]
        for i,a in enumerate(agents.values()):
            colors[a.init_pos] = to_html_color(agent_colors[a.name])
        graph.visualize("Grid Visualization",colors=colors,show_distances=False,show_isolated=False)
    pressed = defaultdict(bool)
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("black")
        for y,row in enumerate(graph.cells):
            for x,c in enumerate(row):
                if c != GridGraph.WALL_CHAR:
                    pygame.draw.rect(screen, "white", (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        
        for aname, agent in agents.items():
            color = agent_colors[aname]
            x,y = graph.coords_from_id(agent.get_position(agent_time))
            pygame.draw.circle(screen, color, ((x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE), 0.4 * TILE_SIZE)
            gx,gy = graph.coords_from_id(agent.goal)
            pygame.draw.line(screen,color,((gx+0.2) * TILE_SIZE, (gy+0.2) * TILE_SIZE), ((gx+0.8) * TILE_SIZE, (gy+0.8) * TILE_SIZE), 5)
            pygame.draw.line(screen,color,((gx+0.8) * TILE_SIZE, (gy+0.2) * TILE_SIZE), ((gx+0.2) * TILE_SIZE, (gy+0.8) * TILE_SIZE), 5)
            sx,sy = graph.coords_from_id(agent.init_pos)
            pygame.draw.circle(screen, color, ((sx + 0.5) * TILE_SIZE, (sy + 0.5) * TILE_SIZE), 0.4 * TILE_SIZE, width=3)

            if SHOW_PATHS:
                for n1, n2 in zip(agent.positions, agent.positions[1:]):
                    x1, y1 = graph.coords_from_id(n1)
                    x2, y2 = graph.coords_from_id(n2)
                    o = agent_offsets[aname]
                    pygame.draw.line(screen,color,((x1+o) * TILE_SIZE, (y1+o) * TILE_SIZE), ((x2+o) * TILE_SIZE, (y2+o) * TILE_SIZE), 2)

        if SHOW_RESERVATIONS:
            for r1,r2 in res[agent_time]:
                x,y = graph.coords_from_id(r1)
                if r1==r2:
                    pygame.draw.rect(screen,(100,100,100),((x + 0.3) * TILE_SIZE, (y + 0.3) * TILE_SIZE, TILE_SIZE * 0.4, TILE_SIZE * 0.4))
                else:
                    x2,y2 = graph.coords_from_id(r2)
                    pygame.draw.polygon(screen,(100,100,100),[((x + 0.3) * TILE_SIZE, (y + 0.3) * TILE_SIZE),((x + 0.7) * TILE_SIZE, (y + 0.7) * TILE_SIZE), ((x2 + 0.5) * TILE_SIZE, (y2 + 0.5) * TILE_SIZE)])
                    pygame.draw.polygon(screen,(100,100,100),[((x + 0.3) * TILE_SIZE, (y + 0.7) * TILE_SIZE),((x + 0.7) * TILE_SIZE, (y + 0.3) * TILE_SIZE), ((x2 + 0.5) * TILE_SIZE, (y2 + 0.5) * TILE_SIZE)])
                
            
        keys = pygame.key.get_pressed()
        lpress = bool(keys[pygame.K_a]) or bool(keys[pygame.K_LEFT])
        if lpress and not pressed["left"]:
            agent_time = max(agent_time - 1, 0)
        pressed["left"] = lpress
        rpress = bool(keys[pygame.K_d]) or bool(keys[pygame.K_RIGHT])
        if rpress and not pressed["right"]:
            agent_time += 1
        pressed["right"] = rpress
        mpress = bool(keys[pygame.K_m])
        if mpress and not pressed["m"]:
            if move_mode == COOP_MODE:
                move_mode = INDEP_MODE
                for a in agents.values(): a.positions = a.optimal_path
            else:
                move_mode = COOP_MODE
                for a in agents.values(): a.positions = a.coop_path
        pressed["m"] = mpress
        ppress = bool(keys[pygame.K_p])
        if ppress and not pressed["p"]:
            SHOW_PATHS = not SHOW_PATHS
        pressed["p"] = ppress
        if keys[pygame.K_0]: agent_time = 0
        if keys[pygame.K_9]: agent_time = max(len(a.positions) for a in agents.values())
                    
        time_render = font.render(f"t = {agent_time}", True, (255,255,255))
        screen.blit(time_render, (5,5))
        success_cnt = sum(1 for a in agents.values() if len(a.positions) > 1)
        success_render = font.render(f"success rate = {success_cnt}/{len(agents)} ({success_cnt/len(agents):.1%})", True, (255,255,255))
        screen.blit(success_render, (80,5))
        screen.blit(controls_render, (5,screen.get_height() - font.get_height() - 2))

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    pygame.quit()