'''
Runs the fixed-policy and learning agents on the physical panel.

'''
# Python imports.
import datetime

# simple_rl imports.
from simple_rl.run_experiments import run_agents_on_mdp
from simple_rl.agents import RandomAgent, FixedPolicyAgent, LinearQLearnerAgent, LinearApproxSarsaAgent, LinUCBAgent


#arduino interface
from interface.ArduinoOOMDP import ArduinoOOMDP
#fixed-policy solar trackers
import sys
sys.path.append("../experiments")
from SolarTrackerArduino import SolarTrackerArduino
import tracking_baselines as tb

def run():
	'''
	runs the experiment on a Grena tracker, for now.
	'''
	
	#set up experiment parameters.
	
	time_per_step = 2.0 #minutes
	
	#create ArduinoOOMDP
	
	current_time = datetime.datetime.now()
	solar_mdp = ArduinoOOMDP(current_time, use_img=True)
	
	
	# Get relevant MDP params.
    actions, gamma, panel_step = solar_mdp.get_actions(), solar_mdp.get_gamma(), solar_mdp.get_panel_step()
    
    #create grena agent
    grena_tracker = SolarTracker(tb.grena_tracker, panel_step=panel_step, dual_axis=False)
    grena_tracker_agent = FixedPolicyAgent(grena_tracker.get_policy(), name="grena-tracker")
    
    

	
	
if __name__=="__main__":
	run()
