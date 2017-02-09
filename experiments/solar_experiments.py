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

    # Todos:
        # Get the simple/grena trackers to output altitude/azimuth
        # Write the policy for the trackers:
            # > Given the altitude/azimuth estimate, make the move that maximizes cos-similarity of sun-vec panel-vec

    dual_axis = True
    image_mode = False

    # Setup MDP.
    panel_step = 2
    date_time = datetime.datetime(day=5, hour=2, month=8, year=2015)
    solar_mdp = SolarOOMDP(date_time, timestep=1.0, panel_step=panel_step, dual_axis = dual_axis, image_mode = image_mode)
    actions = solar_mdp.get_actions()
    gamma = solar_mdp.get_gamma()

    # Setup fixed agents.
    static_agent = FixedPolicyAgent(tb.static_policy)
    random_agent = RandomAgent(actions)

    # Tracker agents.
    good_tracker = SolarTracker(tb.tracker_from_state_info, panel_step=panel_step, dual_axis=dual_axis)
    good_baseline_tracker_agent = FixedPolicyAgent(good_tracker.get_policy(), name="greedy-tracker")

    # Tracker from time/loc.
    # grena_tracker = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=dual_axis)
    # grena_tracker_agent = FixedPolicyAgent(grena_tracker.get_policy(), name="grena-tracker")

    # Simple tracker from time/loc.
    simple_tracker = SolarTracker(tb.simple_tracker, panel_step=panel_step, dual_axis=dual_axis)
    simple_tracker_agent = FixedPolicyAgent(simple_tracker.get_policy(), name="simple-tracker")

    # Setup RL agents.
    lin_approx_agent_rbf = LinearApproxQLearnerAgent(actions, alpha=0.001, epsilon=0.05, gamma=gamma, rbf=True)
    lin_approx_agent = LinearApproxQLearnerAgent(actions, alpha=0.001, epsilon=0.05, gamma=gamma, rbf=False)
    agents = [good_baseline_tracker_agent, static_agent, lin_approx_agent_rbf, lin_approx_agent]

    # Run experiments.
    run_agents_on_mdp(agents, solar_mdp, num_instances=5, num_episodes=1, num_steps=10*60*24)

if __name__ == "__main__":
    main()
