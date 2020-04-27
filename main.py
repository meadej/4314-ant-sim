from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from AntModel import *
from Portrayals import agent_portrayal


def main():
    """
    The main running function.
    :return: 0 on success
    """
    ln_slider = UserSettableParameter('slider', "Number of L. Niger Agents", 2, 0, 100, 1)
    fj_slider = UserSettableParameter('slider', "Number of F. Japonica Agents", 2, 0, 100, 1)
    mk_slider = UserSettableParameter('slider', "Number of M. Kuricola Colonies", 1, 0, 100, 1)
    ft_slider = UserSettableParameter('slider', "Number of F. Tropicalis Colonies", 1, 0, 100, 1)

    grid_width = 30
    grid_height = 30
    # Instantiate the grid the agents will be moving on
    grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 500, 500)
    # Open the visualization server
    server = ModularServer(AntModel,
                           [grid],
                           "L. Niger Model",
                           {"num_ln": ln_slider,
                            "num_fj": fj_slider,
                            "num_mk_col": mk_slider,
                            "num_ft_col": ft_slider,
                            "width": grid_width,
                            "height": grid_height})
    server.port = 8521
    server.launch()
    return 0


if __name__ == "__main__":
    main()