#!/usr/bin/env python

# Python imports.
import subprocess
import random

# Other imports.
import solar_experiments

# Global params.
percept = "angles"
dual_axis = False

def spawn_subproc(location):
	'''
	Args:
		task (str)

	Summary:
		Spawns a child subprocess to run the experiment.
	'''
	cmd = ['python', 'solar_experiments.py', '-loc=' + str(location), '-percept=' + str(percept)]

	if dual_axis:
		cmd.append('-single_axis=True')

	subprocess.Popen(cmd)

def run_average_usa_locs_exp():
	spawn_subproc(location="usa_avg")

def run_iaai_experiments():
	for loc in ["nola", "alaska", "australia", "japan"]:
		spawn_subproc(loc)

def main():
	run_average_usa_locs_exp()

if __name__ == "__main__":
	main()
