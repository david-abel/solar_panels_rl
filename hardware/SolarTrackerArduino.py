'''
Modified solartracker class for arduino actions.
'''

# Python imports.
import numpy as np

# Local imports.
import solarOOMDP.solar_helpers as sh

class SolarTrackerArduino(object):
    ''' Class for a Solar Tracker '''

    def __init__(self, tracker, panel_step, dual_axis=False):
    	self.tracker = tracker
    	self.panel_step = panel_step
    	#self.dual_axis = dual_axis

    def get_policy(self):
    	return self._policy

    def _policy(self, state):
		'''
		Args:
			state (SolarOOMDP state): contains the year, month, hour etc.
			panel_step = int

		Returns:
			(str): Action in the set SolarOOMDPClass.ACTIONS
		'''

		# Compute sun vec. in degrees. 
		sun_az, sun_alt, = self.tracker(state)
		#assuming single-axis panel is oriented on the east-west axis, and forward is to the east, backwards is to the west
		#converting to degrees
		panel_ew, panel_ns = np.degrees(state.get_panel_angle_ew()), np.degrees(state.get_panel_angle_ns())
		print sun_az, sun_alt
		sun_vec = sh._compute_sun_vector(sun_az, sun_alt)
		
		
		print "GRENA PLANNING: desired sun vec: {}".format(sun_vec)
		print "GRENA PLANNING: current panel normal vec: {}".format(sh._compute_panel_normal_vector(panel_ns , panel_ew))

		# Placeholder vars. Modified to reflect arduino action set.
		max_cos_sim = -1
		best_action = "N"
		#NOTE: INVERTED AXIS
		
		#changes rotating along the north south axis, 
		action_effect_dict = {
				"N":(0,0),
				"F":(np.degrees(self.panel_step), 0),
				"B":(np.degrees(-self.panel_step), 0),
			}
		# Find action that minimizes cos difference to estimate of sun vector.
		for action in action_effect_dict.keys():
			delta_ns, delta_ew = action_effect_dict[action]
			panel_vec = sh._compute_panel_normal_vector(panel_ns + delta_ns, panel_ew + delta_ew)
			cos_sim = np.dot(sun_vec, panel_vec)
			
			if cos_sim > max_cos_sim:
				best_action = action
				max_cos_sim = cos_sim

		return best_action

