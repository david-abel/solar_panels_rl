#!/usr/bin/env python

# Python imports.
import subprocess

# Other imports.
import solar_experiments

# Global params.
percept = "cloud"
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
		cmd.append('-dual_axis=True')

	subprocess.Popen(cmd)

def main():

	locations = ["nola"] #["alaska", "australia", "nola", "japan"]

	for loc in locations:
		spawn_subproc(loc)

if __name__ == "__main__":
	main()