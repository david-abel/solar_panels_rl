'''
SolarTrackerClass.py: Contains the SolarTracker class. 
'''

# Python imports.
import numpy as np
import random

# Local imports.
import solarOOMDP.solar_helpers as sh

class SolarTracker(object):
    ''' Class for a Solar Tracker '''

    def __init__(self, tracker, panel_step, actions, dual_axis=False):
        self.tracker = tracker
        self.panel_step = panel_step
        self.dual_axis = dual_axis
        self.actions = actions

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
        sun_alt, sun_az = self.tracker(state)

        sun_vec = sh._compute_sun_vector(sun_alt, sun_az)
        panel_ew, panel_ns = state.get_panel_angle_ew(), state.get_panel_angle_ns()

        # Placeholder vars.
        max_cos_sim = float("-inf")
        best_action = "do_nothing"

        ns_for_effect = 0 if panel_ns ==  90 else self.panel_step
        ns_back_effect = 0 if panel_ns == -90 else -self.panel_step
        ew_for_effect = 0 if panel_ew == 90 else self.panel_step
        ew_back_effect = 0 if panel_ew  == -90 else -self.panel_step

        panel_vec = sh._compute_panel_normal_vector(panel_ns, panel_ew)

        # Find action that minimizes cos difference to estimate of sun vector.
        for action in self.actions:
            panel_vec = action #sh._compute_panel_normal_vector(panel_ns + delta_alt, panel_ew + delta_az)

            cos_sim = np.dot(sun_vec, panel_vec)
            if cos_sim > max_cos_sim:
                best_action = action
                max_cos_sim = cos_sim

        return best_action

