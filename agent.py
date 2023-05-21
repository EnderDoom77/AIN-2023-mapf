class Agent:
    def __init__(self, name, position, goal):
        self.name = name
        self.init_pos = position
        self.positions = [self.init_pos]
        self.goal = goal
        self.optimal_path = []
        self.coop_path = []
    
    def get_position(self, t: int) -> int:
        if t >= len(self.positions):
            return self.positions[-1]
        else:
            return self.positions[t]
        
    def __repr__(self):
        return f"{self.name}: {self.init_pos} -> {self.goal}"