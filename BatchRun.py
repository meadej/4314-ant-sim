from mesa.batchrunner import BatchRunner
from AntModel import AntModel
from DataCollection import ant_state_collector

# Default settings
STEP_COUNT = 300
NUM_LNIGER = 300
NUM_FJAPON = 30
NUM_MK_COL = 5
NUM_FT_COL = 5
GRID_WIDTH = 150
GRID_HEIGHT = 150

fixed_params = {"width": GRID_WIDTH,
                "height": GRID_HEIGHT,
                "num_ln": NUM_LNIGER,
                "num_mk_col": NUM_MK_COL,
                "num_ft_col": NUM_FT_COL}
variable_params = {"num_fj": range(0, 50)}

batch_run = BatchRunner(AntModel,
                        fixed_parameters=fixed_params,
                        variable_parameters=variable_params,
                        iterations=5,
                        max_steps=STEP_COUNT,
                        agent_reporters={"State:": ant_state_collector})
batch_run.run_all()
df = batch_run.get_agent_vars_dataframe()
df.to_csv(path_or_buf="out.csv")