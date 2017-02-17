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

def setup_experiment(exp_name, loc="australia", test_both_axes=False):
    '''
    Args:
        exp_name (str): One of 'sun_percept', 'image_percept', or 'image_cloud_percept'.
    Returns:
        (tuple):
            [1]: (list of Agents)
            [2]: MDP
    '''
    try:
        image_mode, cloud_mode = {
            "sun_percept":(False, False),
            "image_percept":(True, False),
            "image_cloud_percept":(True, True),
        }[exp_name]
    except KeyError:
        print "Error: experiment name unknown ('" + str(exp_name) + "''). Choose one of: ['sun_percept', 'image_percept', 'image_cloud_percept']."
        quit()
    # Setup MDP.
    panel_step = 2
    timestep = 3.0

    # Location.
    if loc == "australia":
        date_time = datetime.datetime(day=1, hour=18, month=6, year=2015)
        lat, lon = -34.25, 142.17
    elif loc == "iceland":
        date_time = datetime.datetime(day=1, hour=18, month=11, year=2030)
        lat, lon = 64.1265, -21.8174
    elif loc == "nyc":
        date_time = datetime.datetime(day=1, hour=18, month=11, year=2025)
        lat, lon = 40.7, 74.006

    solar_mdp = SolarOOMDP(date_time, timestep=timestep, latitude_deg=lat, longitude_deg=lon, panel_step=panel_step, image_mode=image_mode, cloud_mode=cloud_mode)
    actions, gamma = solar_mdp.get_actions(), solar_mdp.get_gamma()
    saxis_actions = solar_mdp.get_single_axis_actions()

    # Setup fixed agent.
    static_agent = FixedPolicyAgent(tb.static_policy, name="fixed-panel")

    # Grena single axis and double axis trackers from time/loc.
    grena_tracker_s = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=False)
    grena_tracker_s_agent = FixedPolicyAgent(grena_tracker_s.get_policy(), name="grena-tracker-single")
    grena_tracker_d = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=True)
    grena_tracker_d_agent = FixedPolicyAgent(grena_tracker_d.get_policy(), name="grena-tracker")

    # Setup RL agents
    lin_ucb_agent_s = LinUCBAgent(saxis_actions, name="lin-ucb-single")
    lin_ucb_agent_d = LinUCBAgent(actions, name="lin-ucb")
    ql_lin_approx_agent_s = LinearApproxQLearnerAgent(saxis_actions, name="ql-lin-single", alpha=0.2, epsilon=0.2, gamma=gamma, rbf=True)
    ql_lin_approx_agent_d = LinearApproxQLearnerAgent(actions, name="ql-lin", alpha=0.2, epsilon=0.2, gamma=gamma, rbf=True)
    sarsa_lin_rbf_agent_s = LinearApproxSarsaAgent(saxis_actions, name="sarsa-lin-single", alpha=0.2, epsilon=0.2, gamma=gamma, rbf=True)
    sarsa_lin_rbf_agent_d = LinearApproxSarsaAgent(actions, name="sarsa-lin", alpha=0.2, epsilon=0.2, gamma=gamma, rbf=True)
    
    if test_both_axes:
        grena_tracker_d_agent.name += "-double"
        lin_ucb_agent_d.name += "-double"
        sarsa_lin_rbf_agent_d.name += "-double"
        ql_lin_approx_agent_d.name += "-double"
        agents = [grena_tracker_s_agent, grena_tracker_d_agent, lin_ucb_agent_s, lin_ucb_agent_d, sarsa_lin_rbf_agent_s, sarsa_lin_rbf_agent_d, ql_lin_approx_agent_s, ql_lin_approx_agent_d]
    else:
        agents = [grena_tracker_d_agent, static_agent, lin_ucb_agent_d, sarsa_lin_rbf_agent_d, ql_lin_approx_agent_d]

    return agents, solar_mdp

def main():

    # Setup experiment parameters, agents, mdp.
    sun_agents, sun_solar_mdp = setup_experiment("sun_percept", loc="nyc", test_both_axes=True)
    img_agents, img_solar_mdp = setup_experiment("image_percept", loc="nyc", test_both_axes=True)
    img_cloud_agents, img_cloud_solar_mdp = setup_experiment("image_cloud_percept", loc="nyc", test_both_axes=True)

    # Run experiments.
    # run_agents_on_mdp(sun_agents, sun_solar_mdp, num_instances=25, num_episodes=1, num_steps=20*24*4, clear_old_results=True)
    # run_agents_on_mdp(img_agents, img_solar_mdp, num_instances=5, num_episodes=1, num_steps=20*24*4, clear_old_results=True)
    run_agents_on_mdp(img_cloud_agents, img_cloud_solar_mdp, num_instances=5, num_episodes=1, num_steps=20*24*4, clear_old_results=True)
    
if __name__ == "__main__":
    main()
