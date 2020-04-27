from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from AntAgents import *
from AphidAgents import *
from uuid import uuid4
import numpy as np


class AntModel(Model):
    def __init__(self, num_ln, num_fj, num_mk_col, num_ft_col, width, height):
        """
        :param num_ln: Number of L. Niger agents
        :param num_fj: Number of F. Japonica agents
        :param num_mk_col: Number of M. Kuricola colonies
        :param num_ft_col: Number of F. Tropicalis colonies
        :param width: Width of the model grid
        :param height: Height of the model grid
        """
        self.num_ln = num_ln
        self.num_fj = num_fj
        self.num_mk_col = num_mk_col
        self.num_ft_col = num_ft_col
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        for i in range(self.num_ln):
            ant = LNiger(uuid4(), self)
            self.schedule.add(ant)
            self.grid.place_agent(ant, self.grid.find_empty())

        for h in range(self.num_fj):
            ant = FJaponica(uuid4(), self)
            self.schedule.add(ant)
            self.grid.place_agent(ant, self.grid.find_empty())

        for j in range(self.num_mk_col):
            colony = MKuricolaColony(uuid4(), self)
            self.schedule.add(colony)
            self.grid.place_agent(colony, self.grid.find_empty())

        for k in range(self.num_ft_col):
            colony = FTropicalisColony(uuid4(), self)
            self.schedule.add(colony)
            self.grid.place_agent(colony, self.grid.find_empty())

    def drop_pheromone(self, location):
        """
        Drops a LNPheromone object at the given location if one does not already exist. If one does already exist,
        1 is added to the existing object's 'tracks' field.
        :param location: An (x, y) tuple detailing the location to drop the pheromone.
        :return: None
        """
        if not self.is_pheromone_in_cell(location):
            self.grid.place_agent(LNPheromone(uuid4(), self), location)
        else:
            self.get_pheromone_in_cell(location).tracks += 1

    def is_pheromone_in_cell(self, location):
        """
        Determines if a pheromone already exists in a given cell.
        :param location: The location to check.
        :return: boolean
        """
        return True in [type(x) == LNPheromone for x in self.grid.get_cell_list_contents(location)]

    def is_ant_in_cell(self, location):
        """
        Determines whether an ant exists in a given cell.
        :param location: The location to check.
        :return: boolean
        """
        return True in [isinstance(x, Ant) for x in self.grid.get_cell_list_contents(location)]

    def is_colony_in_cell(self, location):
        """
        Determines whether an aphid colony exists in a given cell.
        :param location: The location to check.
        :return: boolean
        """
        return True in [type(x) == MKuricolaColony or type(x) == FTropicalisColony
                        for x in self.grid.get_cell_list_contents(location)]

    def get_pheromone_in_cell(self, location):
        """
        Returns a LNPheromone object from a cell. ASsumes the cell has already been proven to have a pheromone object
        in it.
        :param location: The cell location to check.
        :return: The LNPheromone object within the cell.
        """
        in_cell_pheromone = None
        for i in self.grid.get_cell_list_contents(location):
            if type(i) == LNPheromone:
                in_cell_pheromone = i
        return in_cell_pheromone

    def get_closest_agent_of_type(self, agent, agent_type):
        """
        Gets the closest agent (besides self) of type agent_type. Returns -1 if it cannot find one.
        :param agent: The agent to find the closest agent_type to.
        :param agent_type: The type of the agent we are looking for.
        :return:
        """
        for radius in range(1, self.grid.width):
            for neighbor in self.grid.get_neighbors(pos=agent.pos, moore=True, include_center=False, radius=radius):
                if isinstance(neighbor, agent_type):
                    return neighbor
        return -1

    def get_closest_colony(self, agent):
        """
        Gets the closest colony to an agent. If an agent is of type colony, it returns itself.
        :param agent: The agent to find the closest colony to.
        :return: The closest colony or -1 if not found.
        """
        return self.get_closest_agent_of_type(agent, Colony)

    @staticmethod
    def distance_between_cells(location_a, location_b):
        """
        Calculates the distance between two cells on the grid.
        :param location_a: First cell location.
        :param location_b: Second cell location.
        :return:
        """
        return np.sqrt((location_a[0] - location_b[0])**2 + (location_a[1] - location_a[1])**2)

    def get_next_cell_in_direction_of_location(self, goal_cell, possible_cells):
        """
        Returns the cell from a list of possible cells which is closest to the end location.
        :param goal_cell: The goal cell of the agent
        :param possible_cells: Candidate cells.
        :return: The location of the closest cell to the goal cell.
        """
        closest_neighbor_index = -1
        closest_neighbor_distance = np.inf
        for i in range(0, len(possible_cells)):
            dist = self.distance_between_cells(possible_cells[i], goal_cell)
            if dist < closest_neighbor_distance:
                closest_neighbor_index = i
                closest_neighbor_distance = dist
        return possible_cells[closest_neighbor_index]

    def step(self):
        """
        A method called every step that occurs
        :return: None
        """
        self.schedule.step()
