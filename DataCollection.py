from AntAgents import LNiger


def ant_state_collector(agent: LNiger):
    if isinstance(agent, LNiger):
        return agent.activity_state, agent.aggro_state
