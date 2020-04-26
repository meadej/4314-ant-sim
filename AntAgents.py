from mesa import Agent
import random

class LNiger(Agent):
    """
    A model representing the ant studied by our paper, L. Niger.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        """
        A method called every step of the simulation.
        :return: None
        """
        # Gather viable (i.e., empty) steps
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )

        step_weights = []
        for cell in possible_steps:
            if self.model.is_ant_in_cell(cell):
                step_weights.append(0)
            else:
                if self.model.is_pheromone_in_cell(cell):
                    step_weights.append(self.model.get_pheromone_in_cell(cell).tracks)
                else:
                    step_weights.append(1)

        # Drop a pheromone at our current position
        self.drop_pheromone(self.pos)
        # Choose a new position based on surrounding pheromones and move there
        new_position = random.choices(possible_steps, weights=step_weights, k=1)[0]
        self.model.grid.move_agent(self, new_position)

    def drop_pheromone(self, grid_location):
        self.model.drop_pheromone(grid_location)


class FJaponica(Agent):
    """
    An agent representing the natural enemy/predator of L. Niger, F. Japonica.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class LNPheromone(Agent):
    """
    An agent representing a pheromone dropped by L. Niger. Used to help build trails.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.tracks = 1

    def step(self):
        pass
