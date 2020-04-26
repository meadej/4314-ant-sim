from mesa import Agent


class MKuricolaColony(Agent):
    """
    An agent representing a colony of M. Kuricola aphids.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class FTropicalisColony(Agent):
    """
    An agent representing a colony of F. Tropicalis aphids.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
