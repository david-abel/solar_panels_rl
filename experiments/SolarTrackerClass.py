'''
SolarTrackerClass.py: Contains the SolarTracker class. 
'''

class SolarTracker(object):
    ''' Class for a Solar Tracker '''

    def __init__(self, tracker, panel_step):
    	self.tracker = tracker
    	self.panel_step = panel_step

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

		ns_diff = state.get_delta_angle_NS()
		ew_diff = state.get_delta_angle_EW()

		if max(ns_diff, ew_diff) < self.panel_step:
			return "doNothing"
		elif abs(ns_diff) > abs(ew_diff) and ns_diff > 0:
			return "panelBackNS"
		elif abs(ns_diff) < abs(ew_diff) and ew_diff > 0:
			return "panelForwardNS"
		elif abs(ns_diff) > abs(ew_diff) and ns_diff < 0:
			return "panelBackEW"
		else:
			return "panelForwardEW"
