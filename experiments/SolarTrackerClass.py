'''
SolarTrackerClass.py: Contains the SolarTracker class. 
'''

# Python imports.
import numpy

# Local imports.
import solarOOMDP.solar_helpers as sh

class SolarTracker(object):
    ''' Class for a Solar Tracker '''

    def __init__(self, tracker, panel_step, dual_axis=False):
    	self.tracker = tracker
    	self.panel_step = panel_step
    	self.dual_axis = dual_axis

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

		# Compute sun vec.
		sun_az, sun_alt, = self.tracker(state)
		panel_az, panel_alt = state.get_panel_angle_AZ(), state.get_panel_angle_ALT()
		sun_vec = sh._compute_sun_vector(sun_az, sun_alt)

		# Placeholder vars.
		max_cos_diff = 0
		best_action = "doNothing"
		action_effect_dict = {
			"doNothing":(0,0),
			"panelForwardALT":(self.panel_step, 0),
			"panelForwardAZ":(0, self.panel_step),
			"panelBackALT:":(-self.panel_step, 0),
			"panelBackAZ":(0, -self.panel_step)
		}

		# Find action that minimizes cos difference to estimate of sun vector.
		for action in action_effect_dict.keys():
			delta_alt, delta_az = action_effect_dict[action]
			panel_vec = sh._compute_panel_normal_vector(panel_alt + delta_alt, panel_az + delta_az)
			cos_diff = numpy.dot(sun_vec, panel_vec)
			if cos_diff > max_cos_diff:
				best_action = action

		return action

