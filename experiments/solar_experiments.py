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

def setup_experiment(exp_name):
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
    dual_axis = True
    panel_step = 2
    timestep = 4.0
    date_time = datetime.datetime(day=4, hour=20, month=7, year=2015) # Normally: 20
    solar_mdp = SolarOOMDP(date_time, timestep=timestep, panel_step=panel_step, dual_axis = dual_axis, image_mode=image_mode, cloud_mode=cloud_mode)
    actions, gamma = solar_mdp.get_actions(), solar_mdp.get_gamma()

    # Setup fixed agent.
    static_agent = FixedPolicyAgent(tb.static_policy)

    # Grena tracker from time/loc.
    grena_tracker = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=dual_axis)
    grena_tracker_agent = FixedPolicyAgent(grena_tracker.get_policy(), name="grena-tracker")

    # Setup RL agents.
    lin_approx_agent = LinearApproxQLearnerAgent(actions, alpha=0.1, epsilon=0.2, gamma=gamma, rbf=False, anneal=True)
    lin_approx_agent_rbf = LinearApproxQLearnerAgent(actions, alpha=0.1, epsilon=0.2, gamma=gamma, rbf=True, anneal=True)

    agents = [grena_tracker_agent, static_agent, lin_approx_agent_rbf]

    return agents, solar_mdp

def main():

    # Setup experiment parameters, agents, mdp.
    sun_agents, sun_solar_mdp = setup_experiment("sun_percept")
    img_agents, img_solar_mdp = setup_experiment("image_percept")
    img_cloud_agents, img_cloud_solar_mdp = setup_experiment("image_cloud_percept")

    # Run experiments.
    # run_agents_on_mdp(sun_agents, sun_solar_mdp, num_instances=5, num_episodes=1, num_steps=15*24*6, clear_old_results=True)
    # run_agents_on_mdp(img_agents, img_solar_mdp, num_instances=5, num_episodes=1, num_steps=15*24*6, clear_old_results=True)
    run_agents_on_mdp(img_cloud_agents, img_cloud_solar_mdp, num_instances=2, num_episodes=1, num_steps=15*24*2, clear_old_results=True)
    
if __name__ == "__main__":
    main()
