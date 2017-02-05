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

def main():
    # Setup MDP.
    panel_step = 10
    date_time = datetime.datetime(day=5, hour=2, month=8, year=2015)
    solar_mdp = SolarOOMDP(date_time, timestep=0.1, panel_step=panel_step)
    actions = solar_mdp.get_actions()
    gamma = solar_mdp.get_gamma()

    dual_axis = True

    # Setup fixed agent.
    static_agent = FixedPolicyAgent(tb.static_policy)
    random_agent = RandomAgent(actions)

    # Tracker agents.
    good_tracker = SolarTracker(tb.tracker_from_state_info, panel_step=panel_step, dual_axis=dual_axis)
    good_baseline_tracker_agent = FixedPolicyAgent(good_tracker.get_policy(), name="optimal-tracker")

    # Setup RL agents.
    lin_approx_agent_rbf = LinearApproxQLearnerAgent(actions, alpha=0.01, epsilon=0.1, gamma=gamma, rbf=True)
    lin_approx_agent = LinearApproxQLearnerAgent(actions, alpha=0.01, epsilon=0.1, gamma=gamma, rbf=False)
    agents = [static_agent, random_agent, lin_approx_agent_rbf, lin_approx_agent]

    # Run experiments.
    run_agents_on_mdp(agents, solar_mdp, num_instances=1, num_episodes=1, num_steps=60*10*24)

if __name__ == "__main__":
    main()
