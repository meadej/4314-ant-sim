import random
from enum import Enum
import numpy as np
from AphidAgents import *

LIGHT_TRAIL_INTERVAL = range(6, 15)
MEDIUM_TRAIL_INTERVAL = range(51, 64)
HEAVY_TRAIL_INTERVAL = range(98, 127)
BASE_MODEL_SWITCH = 1


class ActivityState(Enum):
    TRAVEL_SOLO = 0
    TRAVEL_LIGHT = 1
    TRAVEL_MEDIUM = 2
    TRAVEL_HEAVY = 3
    TEND_MK = 4
    TEND_FT = 5


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
        self.activity_state = ActivityState.TRAVEL_SOLO

        # A variable describing how attracted this ant is to aphid colonies and regular pheromones
        self.colony_step_weight = 15
        self.pheromone_step_weight = 10

        # A variable describing the radius from which this ant will identify a threat
        self.threat_search_radius = 1

        # A variable describing the radius from which this ant will count "nearby" nestmates
        self.nestmate_search_radius = 4

        # A variable describing the radius an ant has to be at from a colony to be "tending" that colony
        self.colony_tending_radius = 4

        # Variable describing the number of "nearby" nestmates
        self.nearby_nestmates = 0

    def _init_post_place(self):
        """
        An initialization method to be run after the agent is placed.
        :return: None
        """
        # Gets the colony closest to its initial position
        self.closest_colony_location = self.model.get_closest_colony(self).pos

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

        step_weights = self.calculate_step_weights(possible_steps)

        step_weights = self.reduce_step_weights_above_threshold(50, step_weights)

        # Drop a pheromone at our current position
        self.drop_pheromone(self.pos)

        # Choose a new position and move there
        if sum(step_weights) != 0:
            new_position = random.choices(possible_steps, weights=step_weights, k=1)[0]
            self.model.grid.move_agent(self, new_position)

        # Update internal states
        self.update_state()

    @staticmethod
    def reduce_step_weights_above_threshold(threshold, weights):
        """
        A method to reduce the weights of steps that rise above a certain threshold. This method is useful for loop
        avoidance, e.g. making sure an ant doesn't just bounce between two highly-weighted pheromones.
        Currently the method just cuts these weights in half, but there are other methods that could be implemented
        to accomplish the same task.
        :param threshold: The threshold at which any weight equal to or above it will be reduced.
        :param weights: The weights to test.
        :return: A list of altered weights.
        """
        for weight_index in range(0, len(weights)):
            if weights[weight_index] >= threshold:
                weights[weight_index] = weights[weight_index] / 2
        return weights

    def calculate_step_weights(self, possible_steps):
        """
        A method to calculate appropriate probability weights for each possible step the ant may take next.
        :param possible_steps: A list of coordinate tuples of length i representing the possible next steps the
        ant may take.
        :return: A list of weights of length i representing the probability that the ant should take that step.
        """
        step_weights = []
        for cell in possible_steps:
            if self.model.is_ant_in_cell(cell):
                step_weights.append(0)
            else:
                if self.model.is_pheromone_in_cell(cell):
                    step_weights.append(self.pheromone_step_weight * self.model.get_pheromone_in_cell(cell).tracks)
                else:
                    step_weights.append(1)

        # Weight the neighboring cell nearest to the closest colony a little extra so we have a higher
        # probability of traveling in that direction.
        # This step in particular takes up huge amounts of calculation power and time.
        colony_weight = max(step_weights) * self.colony_step_weight

        closest_neighbor = self.model.get_nearest_cell_to_goal(self.closest_colony_location, possible_steps)
        closest_neighbor_index = possible_steps.index(closest_neighbor)
        step_weights[closest_neighbor_index] = \
            step_weights[closest_neighbor_index] + colony_weight if step_weights[closest_neighbor_index] != 0 else 0

        return step_weights

    def drop_pheromone(self, grid_location):
        """
        Drops a LNPheromone object at the specified location.
        :param grid_location: Location to drop.
        :return: None
        """
        self.model.drop_pheromone(grid_location)

    def get_number_colonies_nearby(self, radius):
        """
        Gets the number of aphid colonies nearby self in radius 'radius'.
        :param radius: Number of cells outward to search.
        :return: int
        """
        return self.model.get_number_of_agents_in_radius(self.pos, radius, Colony)

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

    def update_aggro_state_base_model(self):
        """
        Updates our aggressiveness state. 
        The following probability data was all gathered from Sakata and Katayama's paper.
        :return: None
        """
        weights = ()
        if self.get_number_threats_nearby(self.threat_search_radius) == 0:
            # No threats around
            self.aggro_state = AggroState.NO_THREAT
            return
        elif self.activity_state == ActivityState.TRAVEL_SOLO:
            weights = (0.45, 0.2, 0.1, 0.1, 0.15, 0.0)
        elif self.activity_state == ActivityState.TRAVEL_LIGHT:
            weights = (0.32, 0.32, 0.1, 0.12, 0.14, 0.0)
        elif self.activity_state == ActivityState.TRAVEL_MEDIUM:
            weights = (0.21, 0.18, 0.22, 0.1, 0.23, 0.05)
        elif self.activity_state == ActivityState.TRAVEL_HEAVY:
            weights = (0.12, 0.2, 0.12, 0.08, 0.48, 0.0)
        elif self.activity_state == ActivityState.TEND_MK:
            weights = (0.12, 0.08, 0.12, 0.13, 0.45, 0.1)
        elif self.activity_state == ActivityState.TEND_FT:
            weights = (0.02, 0.03, 0.07, 0.02, 0.64, 0.22)

        self.aggro_state = random.choices(list(AggroState)[1:], weights=weights, k=1)

    def update_aggro_state_new_model(self):
        """
        Updates our aggressiveness state.
        The following probability data was generated by our modeling.
        :return: None
        """
        if self.get_number_threats_nearby(self.threat_search_radius) == 0:
            # No threats around
            self.aggro_state = AggroState.NO_THREAT
            return

        aggro_state_str_mapping = {
            " [<AggroState.BITE: 5>]": AggroState.BITE,
            " [<AggroState.FLEE: 1>]": AggroState.FLEE,
            " [<AggroState.NO_RESPONSE: 2>]": AggroState.NO_RESPONSE,
            " [<AggroState.WEAK_RESPONSE: 3>]": AggroState.WEAK_RESPONSE,
            " [<AggroState.LIGHT_BITE_FLEE: 4>]": AggroState.LIGHT_BITE_FLEE,
            " [<AggroState.BITE_ACID: 6>]": AggroState.BITE_ACID

        }
        num_nestmates_nearby = self.get_number_nestmates_nearby(self.nestmate_search_radius)
        choice_weights = [self.model.weights_dict[num_nestmates_nearby][key] for
                          key in self.model.weights_dict[num_nestmates_nearby].keys()]
        aggro_state_str = random.choices(self.model.weights_dict[num_nestmates_nearby],
                                              weights=choice_weights,
                                              k=1)

        self.aggro_state = aggro_state_str_mapping[aggro_state_str]

    def update_aggro_state(self):
        """
        Updates our aggressiveness state. This is where the probability magic happens.
        :return: None
        """
        if BASE_MODEL_SWITCH:
            self.update_aggro_state_base_model()
        else:
            self.update_aggro_state_new_model()

    def get_average_number_surrounding_pheromones(self, radius=1):
        """
        A method that returns the average of all the pheromone counts within a circle of radius radius.
        :return: The average number of surrounding pheromones, rounded up to the closest int.
        """
        total_surrounding_pher = 0
        surrounding_pher_count = 0
        for agent in self.model.grid.get_neighbors(self.pos, moore=True, radius=radius):
            if isinstance(agent, LNPheromone):
                total_surrounding_pher += agent.tracks
                surrounding_pher_count += 1
        average_surrounding_pher = np.ceil(total_surrounding_pher / surrounding_pher_count)
        return average_surrounding_pher

    def update_activity_state(self):
        """
        Updates our activity state - are we traveling on a light, medium, or heavy trail or are we tending a colony.
        :return: None
        """
        # Check if we're actively tending any colonies and, if so, what type of colony.
        if self.get_number_colonies_nearby(self.colony_tending_radius) > 0:
            closest_colony = self.model.get_closest_colony(self)
            if isinstance(closest_colony, FTropicalisColony):
                self.activity_state = ActivityState.TEND_FT
            if isinstance(closest_colony, MKuricolaColony):
                self.activity_state = ActivityState.TEND_MK
            return

        # If we're not tending colonies, see how we're traveling.
        average_surrounding_pher = self.get_average_number_surrounding_pheromones()
        if average_surrounding_pher in LIGHT_TRAIL_INTERVAL:
            self.activity_state = ActivityState.TRAVEL_LIGHT
        elif average_surrounding_pher in MEDIUM_TRAIL_INTERVAL:
            self.activity_state = ActivityState.TRAVEL_MEDIUM
        elif average_surrounding_pher in HEAVY_TRAIL_INTERVAL:
            self.activity_state = ActivityState.TRAVEL_HEAVY
        else:
            self.activity_state = ActivityState.TRAVEL_SOLO

    def update_state(self):
        """
        Update our internal state. We update our trail state first because our agressiveness,
        depending on the factors we are considering, may depend on what type of trail we are on.z
        :return: None
        """
        self.update_activity_state()
        self.update_aggro_state()
        self.nearby_nestmates = self.get_number_nestmates_nearby(self.nestmate_search_radius)


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
        for cell in possible_steps:
            # Do not move to a neighboring cell with another ant already in it
            if self.model.is_ant_in_cell(cell):
                step_weights.append(0)
            else:
                step_weights.append(1)

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
