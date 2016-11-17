'''
SolarOOMDPClass.py: Contains the SolarOOMDP class. 

From:
    Dietterich, Thomas G. "Hierarchical reinforcement learning with the
    MAXQ value function decomposition." J. Artif. Intell. Res.(JAIR) 13
    (2000): 227-303.

Author: David Abel (cs.brown.edu/~dabel/)
'''

# simple_rl imports.
from ...mdp.oomdp.OOMDPClass import OOMDP
from ...mdp.oomdp.OOMDPObjectClass import OOMDPObject
from SolarOOMDPStateClass import SolarOOMDPState
import math

class SolarStationaryOOMDP(OOMDP):
    ''' Class for a Solar OO-MDP '''

    # Static constants.
    ACTIONS = ["doNothing"]
    ATTRIBUTES = ["angle"]
    CLASSES = ["agent", "sun", "time"]

    def __init__(self, num_angles_sun=3, num_angles_panel=5, sun_start_angle=0, panel_start_angle=0):
        init_state = self._create_init_state(sun_start_angle, panel_start_angle)
        OOMDP.__init__(self, SolarStationaryOOMDP.ACTIONS, self.objects, self._transition_func, self._reward_func, init_state=init_state)
        self.step_sun = 180.0/num_angles_sun
        self.step_panel = 180.0/num_angles_panel

    def _create_init_state(self, sun_angle, panel_angle):
        '''
        Args:
            sun_angle (int)
            panel_angle (int)

        Returns:
            (OOMDP State)
        '''

        self.objects = {attr : [] for attr in SolarStationaryOOMDP.CLASSES}

        # Make agent.
        agent_attributes = {}
        agent_attributes["angle"] = panel_angle
        agent = OOMDPObject(attributes=agent_attributes, name="agent")
        self.objects["agent"].append(agent)

        # Make sun.
        sun_attributes = {}
        sun_attributes["angle"] = sun_angle
        sun = OOMDPObject(attributes=sun_attributes, name="sun")
        self.objects["sun"].append(sun)

        return SolarOOMDPState(self.objects)

    def _reward_func(self, state, action):
        '''
        Args:
            state (OOMDP State)
            action (str)

        Returns
            (float)
        '''
        # Reward is inversly proportional to the distance between the angles of the panel and the sun
        distBetweenSunAndPanel = abs(state.get_sun_angle() - state.get_panel_angle())

        # Reward is cosine distance between the two
        angleToRad = math.pi/180.0
        reward = math.cos(distBetweenSunAndPanel * angleToRad)
        
        # Add penalty for moving at all
        return reward

    def _transition_func(self, state, action):
        '''
        Args:
            (OOMDP State)
            action (str)

        Returns
            (OOMDP State)
        '''
        _error_check(state, action)

        # Update the sun position (increment by one sun step)
        new_sun_angle = (state.get_sun_angle() + self.step_sun) % 180

        # If we do nothing, none of the angles change
        if action == "doNothing":
            return self._create_init_state(new_sun_angle, state.get_panel_angle())
        else:
            print "Error: Unrecognized action! (" + action + ")"
            quit()
        
    def __str__(self):
        return "solarmdp_" + "s-" + str(self.step_sun) + "p-" + str(self.step_panel)
def _error_check(state, action):
    '''
    Args:
        state (State)
        action (str)

    Summary:
        Checks to make sure the received state and action are of the right type.
    '''

    if action not in SolarStationaryOOMDP.ACTIONS:
        print "Error: the action provided (" + str(action) + ") was invalid."
        quit()

    if not isinstance(state, SolarOOMDPState):
        print "Error: the given state (" + str(state) + ") was not of the correct class."
        quit()

def main():
    agent = {"angle": 0}
    sun = {"angle": 0}
    solar_world = SolarStationaryOOMDP(0, 0, agent=agent, sun=sun)

if __name__ == "__main__":
    main()
