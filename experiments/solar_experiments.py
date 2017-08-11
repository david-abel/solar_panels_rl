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
from solarOOMDP.PanelClass import Panel
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
    #panel information
    #panel = Panel(1, 1, 10, 0.22, 1500, 0.10, 0.5, 0.1, 0.5)

    panel = Panel(x_dim=1,
                  y_dim=1,
                  assembly_mass=15, #kg
                  COM_offset=0.1, #meters
                  bearing_friction=0.1, #coeff of friction, totally made up
                  efficiency=0.9,
                  offset_angle=0.25, #radians
                  actuator_force=1500,#TODO: remove, not used
                  actuator_offset_ew=0.1,
                  actuator_mount_ew=0.5,
                  actuator_offset_ns=0.1,
                  actuator_mount_ns=0.5)
    
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
        date_time = datetime.datetime(day=1, hour=1, month=1, year=2015)
        lat, lon = -34.25, 142.17
    elif loc == "iceland":
        date_time = datetime.datetime(day=3, hour=16, month=7, year=2020)
        lat, lon = 64.1265, -21.8174
    elif loc == "nyc":
        date_time = datetime.datetime(day=10, hour=1, month=4, year=2020)
        lat, lon = 40.7, 74.006

    mode_dict = {'dual_axis':True, 'image_mode':image_mode, 'cloud_mode':cloud_mode}

    # Make MDP.
    solar_mdp = SolarOOMDP(date_time=date_time,
                            panel=panel,
                            timestep=10.0, # 10 minutes per timestep.
                            latitude_deg=lat,
                            longitude_deg=lon,
                            panel_step=panel_step,
                            mode_dict=mode_dict)

    return solar_mdp

def _setup_agents(solar_mdp, test_both_axes=False):
    '''
    Args:
        solar_mdp (SolarOOMDP)

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
    grena_tracker = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=True)
    grena_tracker_agent = FixedPolicyAgent(grena_tracker.get_policy(), name="grena-tracker")

    # Setup RL agents
    alpha, epsilon = 0.3, 0.7
    lin_ucb_agent = LinUCBAgent(actions, name="lin-ucb") #, alpha=0.2) #, alpha=0.2)
    ql_lin_approx_agent_g0 = LinearApproxQLearnerAgent(actions, name="ql-lin-g0", alpha=alpha, epsilon=epsilon, gamma=0, rbf=True, anneal=True)
    ql_lin_approx_agent = LinearApproxQLearnerAgent(actions, name="ql-lin", alpha=alpha, epsilon=epsilon, gamma=gamma, rbf=True, anneal=True)
    sarsa_lin_rbf_agent = LinearApproxSarsaAgent(actions, name="sarsa-lin", alpha=alpha, epsilon=epsilon, gamma=gamma, rbf=True, anneal=True)
    random_agent = RandomAgent(actions)
    # Regular experiments.
    agents = [sarsa_lin_rbf_agent, ql_lin_approx_agent, lin_ucb_agent, grena_tracker_agent, static_agent]

    return agents

def setup_experiment(percept_type, loc="australia"):
    '''
    Args:
        percept_type (str): One of 'sun_percept', 'image_percept', or 'image_cloud_percept'.
        loc (str): one of ['australia', 'iceland', 'nyc']

    Returns:
        (tuple):
            [1]: (list of Agents)
            [2]: MDP
    '''

    # Setup MDP, agents
    solar_mdp = _make_mdp(loc, percept_type, panel_step=2.0)
    agents = _setup_agents(solar_mdp)
    
    return agents, solar_mdp

def main():

    # Setup experiment parameters, agents, mdp.
    num_days = 1
    loc, steps = "iceland", 6*24*num_days
    sun_agents, sun_solar_mdp = setup_experiment("sun_percept", loc=loc)

    # # Run experiments.
    run_agents_on_mdp(sun_agents, sun_solar_mdp, instances=5, episodes=1, steps=steps, clear_old_results=True)

    
if __name__ == "__main__":
    main()
