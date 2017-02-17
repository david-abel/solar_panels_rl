#!/usr/bin/env python
'''
Code for running RL + solar tracking experiments.

Author: Emily Reif + David Abel
'''

# Python imports.
import datetime

# simple_rl imports.
from simple_rl.run_experiments import run_agents_on_mdp
from simple_rl.agents import RandomAgent, FixedPolicyAgent, LinearApproxQLearnerAgent

# Local imports.
from solarOOMDP.SolarOOMDPClass import SolarOOMDP
from SolarTrackerClass import SolarTracker
import tracking_baselines as tb

def setup_experiment(exp_name, loc="australia"):
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
    # Reykjavik, Iceland: latitude_deg=64.1265, longitude_deg=-21.8174, day=4, hour=20, month=3, year=2030
    # Mildura, Australia: latitude_deg=-34.25, longitude_deg=142.17, day=3, hour=18, month=6, year=2015
    if loc == "australia":
        date_time = datetime.datetime(day=1, hour=18, month=6, year=2015)
        lat, lon = -34.25, 142.17
    elif loc == "iceland":
        date_time = datetime.datetime(day=1, hour=18, month=11, year=2030)
        lat, lon = 64.1265, -21.8174

    solar_mdp = SolarOOMDP(date_time, \
        timestep=timestep, \
        latitude_deg=lat, \
        longitude_deg=lon, \
        panel_step=panel_step, \
        image_mode=image_mode, \
        cloud_mode=cloud_mode)

    actions, gamma = solar_mdp.get_actions(), solar_mdp.get_gamma()

    # Setup fixed agent.
    static_agent = FixedPolicyAgent(tb.static_policy)

    # Grena single axis and double axis trackers from time/loc.
    # grena_tracker_single = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=False)
    # grena_tracker_single_agent = FixedPolicyAgent(grena_tracker_single.get_policy(), name="grena-tracker-single")
    grena_tracker_double = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=True)
    grena_tracker_double_agent = FixedPolicyAgent(grena_tracker_double.get_policy(), name="grena-tracker")

    # Setup RL agents
    saxis_actions = solar_mdp.get_single_axis_actions()
    lin_approx_agent_rbf = LinearApproxQLearnerAgent(actions, alpha=0.2, epsilon=0.2, gamma=gamma, rbf=True)
    lin_approx_agent_single_rbf = LinearApproxQLearnerAgent(saxis_actions, name="linear-single-rbf", alpha=0.2, epsilon=0.2, gamma=gamma, rbf=True)

    # Setup optimal agent
    optimal_agent = FixedPolicyAgent(tb.optimal_policy)
    agents = [optimal_agent, grena_tracker_double_agent, lin_approx_agent_single_rbf, lin_approx_agent_rbf]

    return agents, solar_mdp

def main():

    # Setup experiment parameters, agents, mdp.
    sun_agents, sun_solar_mdp = setup_experiment("sun_percept")
    img_agents, img_solar_mdp = setup_experiment("image_percept")
    img_cloud_agents, img_cloud_solar_mdp = setup_experiment("image_cloud_percept")

    # # Run experiments.
    steps = 5*24*4#20*24*4
    # run_agents_on_mdp(sun_agents, sun_solar_mdp, num_instances=5, num_episodes=1, num_steps=20*24*4, clear_old_results=True)
    # run_agents_on_mdp(img_agents, img_solar_mdp, num_instances=5, num_episodes=1, num_steps=20*24*4, clear_old_results=True)
    run_agents_on_mdp(img_agents, img_solar_mdp, num_instances=5, num_episodes=1, num_steps=steps)
    run_agents_on_mdp(img_agents, img_solar_mdp, num_instances=5, num_episodes=1, num_steps=steps)
    # run_agents_on_mdp(img_cloud_agents, img_cloud_solar_mdp, num_instances=5, num_episodes=1, num_steps=20*24*4, clear_old_results=True)
    # run_agents_on_mdp(img_cloud_agents, img_cloud_solar_mdp, num_instances=5, num_episodes=1, num_steps=20*24*4, clear_old_results=True)
    run_agents_on_mdp(img_cloud_agents, img_cloud_solar_mdp, num_instances=5, num_episodes=1, num_steps=steps)
    run_agents_on_mdp(img_cloud_agents, img_cloud_solar_mdp, num_instances=5, num_episodes=1, num_steps=steps)
    
if __name__ == "__main__":
    main()
