from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from AntModel import *


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
        portrayal["r"] = 0.5
    elif type(agent) is LNPheromone:
        portrayal["Layer"] = 0
        portrayal["Color"] = "green"
        portrayal["r"] = 0.25
        portrayal["text"] = agent.tracks
        portrayal["text_color"] = "white"

    return portrayal


def main():
    """
    The main running function.
    :return: 0 on success
    """
    grid_width = 15
    grid_height = 15
    # Instantiate the grid the agents will be moving on
    grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 500, 500)
    # Open the visualization server
    server = ModularServer(AntModel,
                           [grid],
                           "L. Niger Model",
                           {"num_ln": 3,
                            "num_fj": 0,
                            "num_mk_col":0,
                            "num_ft_col":0,
                            "width": grid_width,
                            "height": grid_height})
    server.port = 8521
    server.launch()
    return 0


if __name__ == "__main__":
    main()