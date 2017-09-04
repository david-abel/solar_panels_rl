'''
Runs the fixed-policy and learning agents on the physical panel.

'''
# Python imports.
import datetime
import time as t

# simple_rl imports.
from simple_rl.run_experiments import run_agents_on_mdp
#error loading linear q learner agent
from simple_rl.agents import RandomAgent, FixedPolicyAgent, LinearApproxSarsaAgent, LinUCBAgent


#arduino interface
from interface.ArduinoOOMDP import ArduinoOOMDP
#fixed-policy solar trackers
import sys
sys.path.append("../experiments")
from SolarTrackerArduino import SolarTrackerArduino
import tracking_baselines as tb


def save_state(filename, agent, state, action, reward, next_state):
	print "saving log to {}".format(filename)
	with open(filename, 'w') as f:
		outstr = "date: {}\nagent: {} \n state: {} \n action: {}\n reward: {} \n next state: {}".format(state.get_date_time(), agent, state, action, reward, next_state)
		f.write(outstr)

def run():
	'''
	runs the experiment on a Grena tracker, for now.
	'''
	
	#set up experiment parameters.
	
	time_per_step = 1 #minutes
	steps_before_switch = 60
	
	#create ArduinoOOMDP
	
	current_time = datetime.datetime.now()
	arduino_mdp = ArduinoOOMDP(current_time, use_img=True)
	
	
	# Get relevant MDP params.
	#NOTE: these actions and MDP setup assume the single-axis panel is set up to move from east (forward) to west (backward). 
	actions, gamma, panel_step = arduino_mdp.get_actions(), arduino_mdp.get_gamma(), arduino_mdp.get_panel_step()
	
	print "setting up agents"
	#create grena agent
	grena_tracker = SolarTrackerArduino(tb.grena_tracker, panel_step=panel_step, dual_axis=False)
	grena_tracker_agent = FixedPolicyAgent(grena_tracker.get_policy(), name="grena-tracker")
	
	#setup RL agents
	
	alpha, epsilon = 0.3, 0.3
	print "alpha: {}, epsilon: {}".format(alpha, epsilon)
	#TODO: where is this implemented?
	#num_features = arduino_mdp.get_num_state_feats()
	lin_ucb_agent = LinUCBAgent(actions, name="lin-ucb", alpha=0.3)
	
	sarsa_lin_rbf_agent = LinearApproxSarsaAgent(actions, name="sarsa-lin", alpha=alpha, epsilon=epsilon, gamma=gamma, rbf=True, anneal=False)
	random_agent = RandomAgent(actions)
	
	
	#TODO: switch current agent every so often
	agents = [grena_tracker_agent, sarsa_lin_rbf_agent, lin_ucb_agent]
	
	#code derived from run_experiments.py from simple_rl 
	
	state = arduino_mdp.get_init_state()
	
	reward = 0
	
	logs = "logs"
	
	current_agent = 0
	
	steps = 0
	
	
	while (True):
		
		#get agent action
		action = agents[current_agent].act(state, reward)
		
		print "taking action {}".format(action)
		
		#executes on Arduino interface
		reward, next_state = arduino_mdp.execute_agent_action(action)
		
		print "--- {} \n agent {} took action {} and recieved reward {}".format(next_state.get_date_time(), str(agents[current_agent]), action, reward)
		
		
		
		
		save_state("{}/{}_{}.txt".format(logs, next_state.get_date_time(), str(agents[current_agent])), str(agents[current_agent]), state, action, reward, next_state)		
		state = next_state
		
		steps += 1
		
		if steps % steps_before_switch == 0:
			current_agent = (current_agent + 1) % 3
			print "SWITCHING AGENT TO {}".format(str(agents[current_agent]))
		
		print "SLEEPING FOR {} MINUTES".format(time_per_step)
		t.sleep(int(time_per_step*60)) #seconds to minute
		

	
if __name__=="__main__":
	run()
