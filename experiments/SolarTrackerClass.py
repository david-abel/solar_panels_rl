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

		sun_az, sun_alt, panel_az, panel_alt = self.tracker(state)
		
		az_diff = sun_az - panel_az
		alt_diff = sun_alt - panel_alt

		if abs(az_diff) < 5 and abs(alt_diff) < 5:
			return "doNothing"
		# elif abs(az_diff) > abs(alt_diff) and az_diff > 0:
			# return "panelForwardAZ"
		# elif abs(az_diff) > abs(alt_diff) and az_diff < 0:
			# return "panelBackAZ"
		elif abs(az_diff) < abs(alt_diff) and alt_diff > 0:
			return "panelForwardALT"
		else:
			return "panelBackALT"