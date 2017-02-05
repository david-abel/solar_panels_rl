'''
SolarTrackerClass.py: Contains the SolarTracker class. 
'''

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

		sun_az, sun_alt, = self.tracker(state)
		panel_az, panel_alt = state.get_panel_angle_AZ(), state.get_panel_angle_ALT()
		
		az_diff = abs(sun_az - panel_az)
		alt_diff = abs(sun_alt - panel_alt)

		# This doesn't work! It's ***not*** just 

		if az_diff <= self.panel_step and alt_diff <= self.panel_step:
			return "doNothing"
		elif not self.dual_axis or alt_diff > az_diff:
			# Single axis, only move altitude.
			if sun_alt < panel_alt:
				# Sun is behind, tilt back.
				return "panelForwardALT"
			else:
				# Sun is in front, tilt forward.
				return "panelBackALT"
		elif sun_az < panel_az:
			# Sun is behind, rotate back.
			return "panelForwardAZ"
		else:
			# Sun is in front, rotate back.
			return "panelBackALT"

