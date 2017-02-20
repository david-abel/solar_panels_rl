#!/usr/bin/env python
'''
Code for running RL + solar tracking experiments.

Author: Emily Reif + David Abel
'''

# Python imports.
import datetime

# simple_rl imports.
from simple_rl.run_experiments import run_agents_on_mdp
from simple_rl.agents import RandomAgent, FixedPolicyAgent, LinearApproxQLearnerAgent, LinearApproxSarsaAgent, LinUCBAgent

# Local imports.
from solarOOMDP.SolarOOMDPClass import SolarOOMDP
from SolarTrackerClass import SolarTracker
import tracking_baselines as tb

def _make_mdp(loc, percept_type, panel_step, reflective_index=0.5):
    '''
    Args:
        loc (str)
        percept_type (str): One of 'sun_percept', 'image_percept', or 'image_cloud_percept'.
        panel_step (int)

    Returns:
        (solarOOMDP)
    '''
    
    # Percepts.
    try:
        image_mode, cloud_mode, = {
            "sun_percept":(False, False),
            "image_percept":(True, False),
            "image_cloud_percept":(True, True),
        }[percept_type]
    except KeyError:
        print "Error: percept type unknown ('" + str(percept_type) + "''). Choose one of: ['sun_percept', 'image_percept', 'image_cloud_percept']."
        quit()

    # Location.
    if loc == "australia":
        date_time = datetime.datetime(day=1, hour=18, month=6, year=2015)
        lat, lon = -34.25, 142.17
    elif loc == "iceland":
        date_time = datetime.datetime(day=3, hour=16, month=7, year=2020)
        lat, lon = 64.1265, -21.8174
    elif loc == "nyc":
        date_time = datetime.datetime(day=1, hour=18, month=8, year=2018)
        lat, lon = 40.7, 74.006

    # Make MDP.
    solar_mdp = SolarOOMDP(date_time, \
        timestep=3.0, \
        latitude_deg=lat, \
        longitude_deg=lon, \
        panel_step=panel_step, \
        image_mode=image_mode, \
        cloud_mode=cloud_mode, \
        reflective_index=reflective_index)

    return solar_mdp

def _setup_agents(solar_mdp, test_both_axes=False, reflective_index_exp=False):
    '''
    Args:
        solar_mdp (SolarOOMDP)
        reflective_index_exp (bool): If true renames agents according to the reflective_index of the solar_mdp

    Returns:
        (list): of Agents
    '''
    # Get relevant MDP params.
    actions, gamma, panel_step = solar_mdp.get_actions(), solar_mdp.get_gamma(), solar_mdp.get_panel_step()
    saxis_actions = solar_mdp.get_single_axis_actions()

    # Setup fixed agent.
    static_agent = FixedPolicyAgent(tb.static_policy, name="fixed-panel")
    optimal_agent = FixedPolicyAgent(tb.optimal_policy, name="optimal")

    # Grena single axis and double axis trackers from time/loc.
    grena_tracker_s = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=False)
    grena_tracker_s_agent = FixedPolicyAgent(grena_tracker_s.get_policy(), name="grena-tracker-single")
    grena_tracker_d = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=True)
    grena_tracker_d_agent = FixedPolicyAgent(grena_tracker_d.get_policy(), name="grena-tracker")

    # Setup RL agents
    alpha, epsilon = 0.3, 0.1
    lin_ucb_agent_s = LinUCBAgent(saxis_actions, name="lin-ucb-single")
    lin_ucb_agent_d = LinUCBAgent(actions, name="lin-ucb")#, alpha=0.2) #, alpha=0.2)
    ql_lin_approx_agent_s = LinearApproxQLearnerAgent(saxis_actions, name="ql-lin-single-$\gamma=0$", alpha=alpha, epsilon=epsilon, gamma=gamma, rbf=True)
    ql_lin_approx_agent_d = LinearApproxQLearnerAgent(actions, name="ql-lin-g0", alpha=alpha, epsilon=epsilon, gamma=0, rbf=True, anneal=True)
    sarsa_lin_rbf_agent_s = LinearApproxSarsaAgent(saxis_actions, name="sarsa-lin-single", alpha=alpha, epsilon=epsilon, gamma=gamma, rbf=True)
    sarsa_lin_rbf_agent_d = LinearApproxSarsaAgent(actions, name="sarsa-lin", alpha=alpha, epsilon=epsilon, gamma=gamma, rbf=True, anneal=True)

    if test_both_axes:
        # Axis comparison experiment.
        grena_tracker_d_agent.name += "-double"
        lin_ucb_agent_d.name += "-double"
        sarsa_lin_rbf_agent_d.name += "-double"
        ql_lin_approx_agent_d.name += "-double"
        agents = [grena_tracker_s_agent, grena_tracker_d_agent, lin_ucb_agent_s, lin_ucb_agent_d, sarsa_lin_rbf_agent_s, sarsa_lin_rbf_agent_d, ql_lin_approx_agent_s, ql_lin_approx_agent_d]
    elif reflective_index_exp:
        # Reflective index experiment.
        grena_tracker_d_agent.name += "-" + str(solar_mdp.get_reflective_index())
        sarsa_lin_rbf_agent_d.name += "-" + str(solar_mdp.get_reflective_index())
        agents = [grena_tracker_d_agent, sarsa_lin_rbf_agent_d]
    else:
        # Regular experiments.
        # agents = [grena_tracker_d_agent, static_agent, lin_ucb_agent_d, sarsa_lin_rbf_agent_d, ql_lin_approx_agent_d]
        agents = [ql_lin_approx_agent_d] #, sarsa_lin_rbf_agent_d, ql_lin_approx_agent_d]
        # agents = [optimal_agent]

    return agents


def setup_experiment(percept_type, loc="australia", test_both_axes=False, reflective_index=None):
    '''
    Args:
        percept_type (str): One of 'sun_percept', 'image_percept', or 'image_cloud_percept'.
        loc (str): one of ['australia', 'iceland', 'nyc']
        test_both_axes (bool)
        reflective_index_exp (float): If true, runs the reflective index experiment.

    Returns:
        (tuple):
            [1]: (list of Agents)
            [2]: MDP
    '''

    # Setup MDP.
    solar_mdps = []
    if reflective_index is not None:
        solar_mdp = _make_mdp(loc, percept_type, panel_step=2.0, reflective_index=reflective_index)
    else:
        solar_mdp = _make_mdp(loc, percept_type, panel_step=2.0)

    agents = _setup_agents(solar_mdp, test_both_axes=test_both_axes, reflective_index_exp=reflective_index is not None)
    
    return agents, solar_mdp

def main():

    # Setup experiment parameters, agents, mdp.
    # loc, steps = "australia", 20*24*4
    # loc, steps = "nyc", 20*24*10
    loc, steps = "iceland", 20*24*8
    sun_agents, sun_solar_mdp = setup_experiment("sun_percept", loc=loc)
    img_agents, img_solar_mdp = setup_experiment("image_percept", loc=loc) #, reflective_index_exp=True)
    img_cloud_agents, img_cloud_solar_mdp = setup_experiment("image_cloud_percept", loc=loc) # reflective_index=0.1)

    # Axis experiment.
    # daxis_agents, daxis_mdp = setup_experiment("sun_percept", loc="nyc", test_both_axes=True) # reflective_index=0.1)
    # run_agents_on_mdp(daxis_agents, daxis_mdp, num_instances=5, num_episodes=1, num_steps=20*24*5, clear_old_results=True)

    # # Run experiments.
    run_agents_on_mdp(sun_agents, sun_solar_mdp, num_instances=10, num_episodes=1, num_steps=steps, clear_old_results=False)
    run_agents_on_mdp(img_agents, img_solar_mdp, num_instances=10, num_episodes=1, num_steps=steps, clear_old_results=False)
    run_agents_on_mdp(img_cloud_agents, img_cloud_solar_mdp, num_instances=5, num_episodes=1, num_steps=steps, clear_old_results=False)

    # Deterministic agents.
    # run_agents_on_mdp(deterministic_agents, sun_solar_mdp, num_instances=1, num_episodes=1, num_steps=steps, clear_old_results=False)
    # run_agents_on_mdp(deterministic_agents, img_solar_mdp, num_instances=1, num_episodes=1, num_steps=steps, clear_old_results=False)
    # run_agents_on_mdp(img_cloud_agents, img_cloud_solar_mdp, num_instances=10, num_episodes=1, num_steps=steps, clear_old_results=False)

    
if __name__ == "__main__":
    main()
