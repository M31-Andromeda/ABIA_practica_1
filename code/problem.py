
from aima.search import Problem, Node, astar_search
import random

class EnergyNetworkProblem(Problem):
    def __init__(self, initial, goal=None):
        super().__init__(initial, goal)

        