import simple_plot.rl_plot as rp
import argparse
import os
import math
import matplotlib
from collections import defaultdict


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", type = str, default="results/", help = "Path to relevant csv files of data.")
    parser.add_argument("-a", type = bool, default=False, help = "If true, plots average reward (default is cumulative).")
    return parser.parse_args()

def find_pairs(agents):
    agent_pairs = {}
    singles = [a for a in agents if "single" in a]

    for agent in singles:
        core_name = agent.replace("-single","")
        agent_pairs[core_name] = (agent, agent.replace("single","double"))

    return agent_pairs

def compute_pair_diffs_and_cis(agent_pairs, data_dir, cumulative):
    pair_diffs = [[] for alg in agent_pairs]
    
    pair_cis = []
    for i, core_agent_name in enumerate(agent_pairs):
        pair = agent_pairs[core_agent_name]
        if data_dir[-1] == "/":
            data_dir = data_dir[:-1]
        data = rp.load_data(data_dir, pair) # [alg][instance][episode]

        avg_data = rp.average_data(data, cumulative=cumulative)
        for e, episode in enumerate(avg_data[0]):
            # Calculate avg difference between the double and single axes.
            diff = avg_data[1][e] - avg_data[0][e] # Double is [1], Single [0].
            pair_diffs[i] += [diff]

        cis = rp.compute_conf_intervals(data, cumulative=cumulative)

        true_pair_cis = []
        for i in xrange(len(cis[0])):
            new_ci = math.sqrt( (cis[0][i])**2 + (cis[1][i])**2)
            true_pair_cis += [new_ci]
        
        pair_cis += [true_pair_cis]

    return pair_diffs, pair_cis

def main():

    # Parse args.
    args = parse_args()


    font = {'family' : 'sans serif',
        # 'weight' : 'bold',
        'size'   : 14}

    matplotlib.rc('font', **font)

    # Grab agents.
    data_dir = args.dir
    agents = [agent.replace(".csv","") for agent in os.listdir(data_dir) if ".csv" in agent]
    if len(agents) == 0:
        print "Error: no csv files found."
        quit()

    agent_pairs = find_pairs(agents)
    cumulative = not(args.a)
    pair_diffs, pair_cis = compute_pair_diffs_and_cis(agent_pairs, data_dir, cumulative=cumulative)

    # Create plot.
    y_axis_label = "Average Double Axis Reward Advantage"
    title = "Double Axis vs. Single Axis w/ True Sun Angles" # Need to mention percept type.
    rp.plot(pair_diffs, data_dir, agent_pairs, conf_intervals=pair_cis, use_cost=False, cumulative=cumulative, episodic=False, title=title, y_axis_label=y_axis_label)


if __name__ == "__main__":
	main()