from mesa import Agent


class Colony(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class MKuricolaColony(Colony):
    """
    An agent representing a colony of M. Kuricola aphids.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.size = 20

    def step(self):
        """
        Colonies do not move, but may grow.
        :return:
        """
        pass


class FTropicalisColony(Colony):
    """
    An agent representing a colony of F. Tropicalis aphids.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.size = 20

    def step(self):
        """
        Colonies do not move, but may grow.
        :return:
        """
        pass
