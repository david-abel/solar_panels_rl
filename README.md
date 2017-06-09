# solar_panels_rl
Code associated with our paper:
"[Improving Solar Panel Efficiency Using Reinforcement Learning](http://cs.brown.edu/~dabel/papers/solarl.pdf)" presented at RLDM 2017.

Our work focuses on applying reinforcement learning techniques to improve Solar Tracking.

Experiments require [simple_rl](https://github.com/david-abel/simple_rl), which can be installed with the usual:

	pip install simple_rl


## Example

To run a simple example, grab the _setup_solar_experiment_ function from _solar_experiments_, and the _run_agents_on_mdp_ from _simple_rl_:


	# RL Library.
	from simple_rl.run_experiments import run_agents_on_mdp
	from solar_experiments import setup_solar_experiment

	def main():

	    # Setup experiment parameters, agents, mdp.
	    sun_agents, sun_solar_mdp = setup_solar_experiment("sun_percept", loc="nyc")

	    # Run experiments.
	    run_agents_on_mdp(sun_agents, sun_solar_mdp, instances=10, episodes=1, steps=6*24)

	    
	if __name__ == "__main__":
	    main()


Contact david_abel@brown.edu with any questions.
