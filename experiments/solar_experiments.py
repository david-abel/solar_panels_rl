 #!/usr/bin/env python
'''
Code for running RL + solar tracking experiments.

Author: Emily Reif + David Abel
'''

# Python imports.
import datetime
import random
from pytz import timezone
import argparse

# Other imports.
from simple_rl.run_experiments import run_agents_on_mdp
from simple_rl.agents import RandomAgent, FixedPolicyAgent, LinearQLearnerAgent, LinearSarsaAgent, LinUCBAgent, QLearnerAgent
from solarOOMDP.SolarOOMDPClass import SolarOOMDP
from SolarTrackerClass import SolarTracker
from solarOOMDP.PanelClass import Panel
import tracking_baselines as tb

def _make_mdp(loc, percept_type, panel_step, dual_axis=False, time_per_step=15.0, reflective_index=0.35, energy_breakdown_experiment=False):
    '''
    Args:
        loc (str)
        percept_type (str): One of 'sun_percept', 'image_percept', or 'image_cloud_percept'.
        dual_axis (bool)
        time_per_step (float): Time in minutes taken per action.
        reflective_index (float)
        energy_breakdown_experiment (bool): If true tracks energy breakdown.

    Returns:
        (solarOOMDP)
    '''
    #panel information
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
            "sun":(False, False),
            "image":(True, False),
            "cloud":(True, True),
        }[percept_type]
    except KeyError:
        print "Error: percept type unknown ('" + str(percept_type) + "''). Choose one of: ['sun', 'image', 'cloud']."
        quit()

    # Location.
    year = 2020
    if loc == "australia":
        date_time = datetime.datetime(day=23, hour=20, month=11, year=year)
        localtz = timezone('Australia/Sydney')
        lat, lon = -34.25, 142.17
    elif loc == "iceland":
        date_time = datetime.datetime(day=1, hour=1, month=8, year=year)
        localtz = timezone('Iceland')
        lat, lon = 64.1265, -21.8174
    elif loc == "nyc":
        date_time = datetime.datetime(day=1, hour=10, month=6, year=year)
        localtz = timezone('America/New_York')
        lat, lon = 40.7, 74.006
    elif loc == "nola":
        # DON'T CHANGE
        date_time = datetime.datetime(day=1, hour=15, month=5, year=year)
        lat, lon = 30.03, 90.05
        localtz = timezone('America/Kentucky/Louisville')
    elif loc == "pvd":
        # DON'T CHANGE
        date_time = datetime.datetime(day=1, hour=10, month=9, year=year)
        localtz = timezone('America/New_York')
        lat, lon = 41.82399, 71.41283
    elif loc == "rio":
        date_time = datetime.datetime(day=5, hour=10, month=10, year=year)
        localtz = timezone('Brazil/West')
        lat, lon = 22.9068, 43.1729
    elif loc == "japan":
        date_time = datetime.datetime(day=1, hour=10, month=1, year=year)
        localtz = timezone('Japan')
        lat, lon = 35.6895, 139.6917
    elif loc == "alaska":
        date_time = datetime.datetime(day=25, hour=5, month=6, year=year)
        localtz = timezone('US/Alaska')
        lat, lon = 58.3019, 134.4197
    elif loc == "cape_town":
        date_time = datetime.datetime(day=1, hour=10, month=7, year=year)
        localtz = timezone('Africa/Johannesburg')
        lat, lon = 33.9351, 18.4289

    local_date_time = localtz.localize(date_time)

    mode_dict = {'dual_axis':dual_axis, 'image_mode':image_mode, 'cloud_mode':cloud_mode}

    if energy_breakdown_experiment:
        loc += "-energy"

    # Make MDP.
    solar_mdp = SolarOOMDP(name_ext=loc,
                            date_time=local_date_time,
                            panel=panel,
                            timestep=time_per_step,
                            latitude_deg=lat,
                            longitude_deg=lon,
                            panel_step=panel_step,
                            reflective_index=reflective_index,
                            mode_dict=mode_dict)

    return solar_mdp

def _setup_agents(solar_mdp):
    '''
    Args:
        solar_mdp (SolarOOMDP)

    Returns:
        (list): of Agents
    '''
    # Get relevant MDP params.
    actions, gamma, panel_step = solar_mdp.get_actions(), solar_mdp.get_gamma(), solar_mdp.get_panel_step()

    # Setup fixed agent.
    static_agent = FixedPolicyAgent(tb.static_policy, name="fixed-panel")
    optimal_agent = FixedPolicyAgent(tb.optimal_policy, name="optimal")

    # Grena single axis and double axis trackers from time/loc.
    grena_tracker = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=solar_mdp.dual_axis)
    grena_tracker_agent = FixedPolicyAgent(grena_tracker.get_policy(), name="grena-tracker")

    # Setup RL agents
    alpha, epsilon = 0.1, 0.05
    rand_init = True
    num_features = solar_mdp.get_num_state_feats()
    lin_ucb_agent = LinUCBAgent(solar_mdp.get_bandit_actions(), name="lin-ucb", rand_init=rand_init, alpha=2.0)
    sarsa_agent_g0 = LinearSarsaAgent(actions, num_features=num_features, name="sarsa-lin-g0", rand_init=rand_init, alpha=alpha, epsilon=epsilon, gamma=0, rbf=False, anneal=True)
    sarsa_agent = LinearSarsaAgent(actions, num_features=num_features, name="sarsa-lin", rand_init=rand_init, alpha=alpha, epsilon=epsilon, gamma=gamma, rbf=False, anneal=True)
    ql_agent = QLearnerAgent(actions, alpha=alpha, epsilon=epsilon, gamma=gamma)
    random_agent = RandomAgent(actions)
    
    # Regular experiments.
    agents = [lin_ucb_agent, sarsa_agent, sarsa_agent_g0] #, grena_tracker_agent, static_agent] #, optimal_agent]
    # agents = [lin_ucb_agent, grena_tracker_agent] #, sarsa_agent, sarsa_agent_g0, grena_tracker_agent, static_agent] #, optimal_agent]
    # agents = [grena_tracker_agent, static_agent] #, optimal_agent]

    return agents

def setup_experiment(percept_type, loc="australia", dual_axis=False, panel_step=2.0, time_per_step=15.0, reflective_index=0.35, energy_breakdown_experiment=False):
    '''
    Args:
        percept_type (str): One of 'sun_percept', 'image_percept', or 'image_cloud_percept'.
        loc (str): one of ['australia', 'iceland', 'nyc']
        dual_axis (bool)
        panel_step (float)
        time_per_step (float): Time in minutes taken per action.
        reflective_index (float): In [0:1], determines the albedo of the nearby ground.
        energy_breakdown_experiment (bool): If true, tracks which energy types are leading to reward.

    Returns:
        (tuple):
            [1]: (list of Agents)
            [2]: MDP
    '''

    # Setup MDP, agents
    solar_mdp = _make_mdp(loc, percept_type, panel_step=panel_step, dual_axis=dual_axis, time_per_step=time_per_step, reflective_index=reflective_index, energy_breakdown_experiment=energy_breakdown_experiment)
    agents = _setup_agents(solar_mdp)
    
    return agents, solar_mdp



def parse_args():
    '''
    Summary:
        Parse all arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-loc", type = str, default = "alaska", nargs = '?', help = "Choose the location for the experiment.")
    parser.add_argument("-percept", type = str, default = "sun", nargs = '?', help = "One of {sun, image, cloud}.")
    parser.add_argument("-dual_axis", type = bool, default = False, nargs = '?', help = "If true uses dual axis tracker.")
    args = parser.parse_args()

    return args.loc, args.percept, args.dual_axis


def main():

    # Paper experiments:
        # num_days = 1
        # time_per_step = 10
        # panel_step = 5, dual: 20
        # reflective = 0.55
        # instances = 10
        # episodes = 50, dual: 100

    # Setup experiment parameters, agents, mdp.
    num_days = 1
    per_hour = True
    time_per_step = 10.0 # in minutes.
    loc, percept_type, dual_axis = parse_args()
    steps = int(24*(60 / time_per_step)*num_days)
    panel_step = 5
    reflective_index = 0.55

    energy_breakdown_experiment = False

    # If per hour is true, plots every hour long reward chunk, otherwise every day.
    rew_step_count = (steps / num_days ) / 24 if per_hour else (steps / num_days)
    sun_agents, sun_solar_mdp = setup_experiment(percept_type=percept_type, loc=loc, dual_axis=dual_axis, panel_step=panel_step, time_per_step=time_per_step, reflective_index=reflective_index, energy_breakdown_experiment=energy_breakdown_experiment)

    # # Run experiments.
    run_agents_on_mdp(sun_agents, sun_solar_mdp, instances=10, episodes=50, steps=steps, clear_old_results=True, rew_step_count=rew_step_count, verbose=False)


if __name__ == "__main__":
    main()
