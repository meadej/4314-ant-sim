from mesa import Agent
import numpy as np
import random
from enum import Enum

DETAILED_ANALYSIS_SWITCH = 1


class TrailState(Enum):
    LIGHT = 0
    MEDIUM = 0
    HEAVY = 1


class AggroState(Enum):
    NO_THREAT = 0
    FLEE = 1
    NO_RESPONSE = 2
    WEAK_RESPONSE = 3
    LIGHT_BITE_FLEE = 4
    BITE = 5
    BITE_ACID = 6


class Ant(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class LNiger(Ant):
    """
    A model representing the ant studied by our paper, L. Niger.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.aggro_state = AggroState.NO_THREAT
        self.trail_state = TrailState.LIGHT

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

        # Split the highest step weight above a threshold to avoid potential loops
        weight_threshold = 20
        if max(step_weights) > weight_threshold:
            step_weights[step_weights.index(max(step_weights))] = np.ceil(step_weights.index(max(step_weights)) / 2)

        # Weight the neighboring cell nearest to the closest colony a little extra so we have a higher
        # probability of traveling in that direction.
        colony_weight = max(step_weights)
        closest_colony_location = self.model.get_closest_colony(self).pos
        closest_neighbor = self.model.get_next_cell_in_direction_of_location(closest_colony_location, possible_steps)
        closest_neighbor_index = possible_steps.index(closest_neighbor)
        step_weights[closest_neighbor_index] = \
            step_weights[closest_neighbor_index] + colony_weight if step_weights[closest_neighbor_index] != 0 else 0

        # Drop a pheromone at our current position
        self.drop_pheromone(self.pos)
        # Choose a new position and move there
        new_position = random.choices(possible_steps, weights=step_weights, k=1)[0]
        self.model.grid.move_agent(self, new_position)

    def drop_pheromone(self, grid_location):
        """
        Drops a LNPheromone object at the specified location.
        :param grid_location: Location to drop.
        :return: None
        """
        self.model.drop_pheromone(grid_location)

    def get_number_nestmates_nearby(self, radius):
        """
        Gets the number of nestmates nearby self in radius 'radius'.
        :param radius: Number of squares outward to search.
        :return: int
        """
        return self.model.get_number_of_agents_in_radius(self.pos, radius, LNiger)

    def get_number_threats_nearby(self, radius):
        """
        Gets the number of threats extant within radius 'radius'.
        :param radius: Number of squares outward to search.
        :return: int
        """
        return self.model.get_number_of_agents_in_radius(self.pos, radius, FJaponica)

    def update_aggro_state(self):
        """
        Updates our aggressiveness state.
        :return: None
        """
        if self.get_number_threats_nearby(2) == 0:
            self.aggro_state = AggroState.NO_THREAT
            return

    def update_trail_state(self):
        """
        Updates our trail state - i.e. light, medium, or heavy.
        :return: None
        """
        pheromones_on_grid = self.mode.get_all_of_agent_type(LNPheromone)
        pheromone_counts = [t.trails for t in pheromones_on_grid]
        max_pher = max(pheromone_counts)
        light_limit = max_pher / 3
        medium_limit = light_limit * 2
        heavy_limit = max_pher

        total_surrounding_pher = 0
        surrounding_pher_count = 0
        for agent in self.model.grid.get_neighbors(self.pos):
            if isinstance(agent, LNPheromone):
                total_surrounding_pher += agent.tracks
                surrounding_pher_count += 1
        average_surrounding_pher = total_surrounding_pher / surrounding_pher_count

        if average_surrounding_pher <= light_limit:
            self.trail_state = TrailState.LIGHT
        elif light_limit < average_surrounding_pher <= medium_limit:
            self.trail_state = TrailState.MEDIUM
        elif medium_limit < average_surrounding_pher:
            self.trail_state = TrailState.HEAVY

    def update_state(self):
        """
        Update our internal state. We update our trail state first because our agressiveness,
        depending on the factors we are considering, may depend on what type of trail we are on.
        :return:
        """
        self.update_trail_state()
        self.update_aggro_state()


class FJaponica(Ant):
    """
    An agent representing the natural enemy/predator of L. Niger, F. Japonica.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # Gather viable (i.e., empty) steps
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )

        step_weights = []
        prey_weight = 3
        for cell in possible_steps:
            # Do not move to a neighboring cell with another ant already in it
            if self.model.is_ant_in_cell(cell):
                step_weights.append(0)
            else:
                step_weights.append(1)

        # We want to aim towards L. Niger ants.
        closest_prey_location = self.model.get_closest_agent_of_type(self, LNiger).pos
        closest_neighbor = self.model.get_next_cell_in_direction_of_location(closest_prey_location, possible_steps)
        closest_neighbor_index = possible_steps.index(closest_neighbor)
        step_weights[closest_neighbor_index] = prey_weight if step_weights[closest_neighbor_index] != 0 else 0

        # Choose a new position and move there
        new_position = random.choices(possible_steps, weights=step_weights, k=1)[0]
        self.model.grid.move_agent(self, new_position)


class LNPheromone(Agent):
    """
    An agent representing a pheromone dropped by L. Niger. Used to help build trails.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.tracks = 1

    def step(self):
        pass
