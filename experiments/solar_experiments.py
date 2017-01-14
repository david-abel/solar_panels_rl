#!/usr/bin/env python
'''
Code for running RL + solar tracking experiments.

Author: Emily Reif + David Abel
'''

# Python imports.
import time, argparse, os, sys, copy
from collections import defaultdict

# simple_rl imports.
from simple_rl.run_experiments import run_agents_on_mdp
from simple_rl.experiments import Experiment
from simple_rl.agents import RandomAgent, FixedPolicyAgent, QLearnerAgent, LinearApproxQLearnerAgent

# Local imports.
from solarOOMDP.SolarOOMDPClass import SolarOOMDP
from SolarTrackerClass import SolarTracker
import tracking_baselines as tb

def main():
    # Setup MDP.
    panel_step = 1
    solar_mdp = SolarOOMDP(timestep=5, panel_step=panel_step)
    actions = solar_mdp.get_actions()
    gamma = solar_mdp.get_gamma()

    # Setup fixed agents.
    tracker = SolarTracker(tb.simple_tracker, panel_step=panel_step)
    baseline_tracker_agent = FixedPolicyAgent(tracker.get_policy())

    # Setup fixed agents.
    static_agent = FixedPolicyAgent(tb.static_policy)

    # Setup RL agents.
    random_agent = RandomAgent(actions)
    qlearner_agent = QLearnerAgent(actions, gamma=gamma, explore="uniform")
    lin_approx_agent = LinearApproxQLearnerAgent(actions, gamma=gamma, rbf=True)
    agents = [lin_approx_agent, static_agent, random_agent]
    
    # Run experiments.
    run_agents_on_mdp(agents, solar_mdp, num_instances=5, num_episodes=1, num_steps=24*6*25)

if __name__ == "__main__":
    main()
