from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from AntModel import *
from Portrayals import agent_portrayal
from time import time

VISUALIZE_MODEL = False
NUM_SIMS = 5

# Default settings
STEP_COUNT = 1000
NUM_LNIGER = 300
NUM_FJAPON = 100
NUM_MK_COL = 20
NUM_FT_COL = 20
GRID_WIDTH = 100
GRID_HEIGHT = 100


def main():
    """
    The main running function.
    :return: 0 on success
    """
    ln_slider = UserSettableParameter('slider', "Number of L. Niger Agents", NUM_LNIGER, 0, 300, 1)
    fj_slider = UserSettableParameter('slider', "Number of F. Japonica Agents", NUM_FJAPON, 0, 300, 1)
    mk_slider = UserSettableParameter('slider', "Number of M. Kuricola Colonies", NUM_MK_COL, 0, 100, 1)
    ft_slider = UserSettableParameter('slider', "Number of F. Tropicalis Colonies", NUM_FT_COL, 0, 100, 1)

    # Instantiate the grid the agents will be moving on
    grid = CanvasGrid(agent_portrayal, GRID_WIDTH, GRID_HEIGHT, 500, 500)

    if VISUALIZE_MODEL:
        # Open the visualization server
        server = ModularServer(AntModel,
                               [grid],
                               "L. Niger Model",
                               {"num_ln": ln_slider,
                                "num_fj": fj_slider,
                                "num_mk_col": mk_slider,
                                "num_ft_col": ft_slider,
                                "width": GRID_WIDTH,
                                "height": GRID_HEIGHT})
        server.port = 8521
        server.launch()
    else:
        for j in range(NUM_SIMS):
            sim_time_sum = 0
            print("Model Initialization #", str(j))
            s = time()
            model = AntModel(NUM_LNIGER, NUM_FJAPON, NUM_MK_COL, NUM_FT_COL, GRID_WIDTH, GRID_HEIGHT)
            e = time()
            sim_time_sum += e - s
            print(e-s)
            for i in range(STEP_COUNT):
                if i % 10 == 0:
                    print(j, "Step", i)

                s = time()
                model.step()
                e = time()
                sim_time_sum += e - s

                if i % 10 == 0:
                    print(e-s)
            print("Model #", str(j), "complete. Total time", str(sim_time_sum))
            df = model.data_collector.get_agent_vars_dataframe()
            df = df.dropna(axis=0)
            df.to_csv(path_or_buf="out" + str(j) + ".csv")

    return 0


if __name__ == "__main__":
    main()
