from AntAgents import *
from AphidAgents import *


def agent_portrayal(agent):
    """
    Determine how each agent type is portrayed on screen.
    :param agent: The agent being portrayed
    :return: A dictionary with attributes for how to display the agent.
    """
    portrayal = {"Shape": "circle",
                 "Filled": "true"}
    if type(agent) is LNiger:
        portrayal["Layer"] = 0
        portrayal["Color"] = "blue"
        portrayal["r"] = 0.7
    elif type(agent) is FJaponica:
        portrayal["Layer"] = 0
        portrayal["Color"] = "gray"
        portrayal["r"] = 0.8
    elif type(agent) is LNPheromone:
        portrayal["Layer"] = 2
        portrayal["Color"] = "green"
        portrayal["r"] = 0.25
        portrayal["text"] = agent.tracks
        portrayal["text_color"] = "white"
    elif isinstance(agent, Colony):
        portrayal["Layer"] = 1
        portrayal["Color"] = "yellow"
        portrayal["r"] = 0.4

    return portrayal
