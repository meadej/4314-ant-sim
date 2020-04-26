from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from AntAgents import *
import uuid


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
        self.num_lfj = num_fj
        self.num_mk_col = num_mk_col
        self.num_ft_col = num_ft_col
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        for i in range(self.num_ln):
            ant = LNiger(i, self)
            self.schedule.add(ant)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(ant, (x, y))

    def drop_pheromone(self, location):
        """
        Drops a LNPheromone object at the given location if one does not already exist. If one does already exist,
        1 is added to the existing object's 'tracks' field.
        :param location: An (x, y) tuple detailing the location to drop the pheromone.
        :return: None
        """
        if not self.is_pheromone_in_cell(location):
            self.grid.place_agent(LNPheromone(uuid.uuid4(), self), location)
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
        return True in [type(x) == FJaponica or type(x) == LNiger for x in self.grid.get_cell_list_contents(location)]

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

    def step(self):
        """
        A method called every step that occurs
        :return:
        """
        self.schedule.step()
