''' SolarMDPClass.py: Contains the SolarMDPClass class. '''

# Local libs.
from ...mdp.MDPClass import MDP
from SolarStateClass import SolarState
import math

class SolarMDP(MDP):
    ''' Imeplementation for a Solar MDP '''

    ACTIONS = ["panelForward", "panelBack", "doNothing"]

    def __init__(self, num_angles_sun=3, num_angles_panel=5):
        '''
        Args:
            num_angles_sun (int) [optional]: Number of discritized angles the 
            sun can be at (from 0 to 180).
            num_angles_panel (int) [optional]: Number of discritized angles the 
            solar panel can be at (from 0 to 180).
        '''
        MDP.__init__(self, SolarMDP.ACTIONS, self._transition_func, self._reward_func, init_state=SolarState(180.0/num_angles_sun, 0.0))
        self.step_sun = 180.0/num_angles_sun
        self.step_panel = 180.0/num_angles_panel

    def _reward_func(self, state, action):
        '''
        Args:
            state (State)
            action (str)
            statePrime

        Returns
            (float)
        '''
        # print "sun, panel: " + str(state.angle_sun) + " : " + str(state.angle_panel)
        # Reward is inversly proportional to the distance between the angles of the panel and the sun
        distBetweenSunAndPanel = abs(state.angle_sun - state.angle_panel)

        # Reward is cosine distance between the two
        angleToRad = math.pi/180.0
        reward = math.cos(distBetweenSunAndPanel * angleToRad)

        # Add penalty for moving at all
        if ((action == 'panelForward') | (action == 'panelBack')):
            reward -= 0.05
        return reward

    def _transition_func(self, state, action):
        '''
        Args:
            state (State)
            action (str)

        Returns
            (State)
        '''

        # Update the sun position (increment by one sun step)
        new_sun_angle = (state.angle_sun + self.step_sun) % 180

        # If we move the panel forward, increment panel angle by one step
        if action == "panelForward":
            new_panel_angle = min(state.angle_panel + self.step_panel, 180.0)
            return SolarState(new_sun_angle, new_panel_angle)

        # If we move the panel back, decrement panel angle by one step
        elif action == "panelBack":
            new_panel_angle = max(state.angle_panel - self.step_panel, 0.0)
            return SolarState(new_sun_angle, new_panel_angle)

        # If we do nothing, none of the angles change
        elif action == "doNothing":
            return SolarState(new_sun_angle, state.angle_panel)
        else:
            print "Error: Unrecognized action! (" + action + ")"
            quit()

    def __str__(self):
        return "solarndp"
        #return "solarmdp_" + "s-" + str(self.num_angles_sun) + "p-" + str(self.num_angles_panel)

