'''
SolarOOMDPClass.py: Contains the SolarOOMDP class. 

Author: Emily Reif
'''

# simple_rl imports.
from simple_rl.mdp.oomdp.OOMDPClass import OOMDP
from simple_rl.mdp.oomdp.OOMDPObjectClass import OOMDPObject
from SolarOOMDPStateClass import SolarOOMDPState
import math
from pysolar import solar, radiation
import datetime

class SolarOOMDP(OOMDP):
    ''' Class for a Solar OO-MDP '''

    # Static constants.
    ACTIONS = ["panelForward", "panelBack", "doNothing"]
    ATTRIBUTES = ["angle"]
    CLASSES = ["agent", "time"]

    #timestep is in minutes, for now
    def __init__(self, timestep=30, panel_step=20, time_start=0, panel_start_angle=0):
        self.time = datetime.datetime(2016, 11, 4, 0, time_start)
        init_state = self._create_state(panel_start_angle, self.time)
        OOMDP.__init__(self, SolarOOMDP.ACTIONS, self.objects, self._transition_func, self._reward_func, init_state=init_state)

        # Global information
        self.latitude_deg = 42.3 # positive in the northern hemisphere
        self.longitude_deg = -71.4 # negative reckoning west from prime meridian in Greenwich, England
        self.step_panel = panel_step
        self.timestep = timestep

    def _get_radiation(self, utc_datetime, altitude_deg, panel_angle):
        if(altitude_deg > 0):
            day = solar.GetDayOfYear(utc_datetime)
            flux = radiation.GetApparentExtraterrestrialFlux(day)
            optical_depth = radiation.GetOpticalDepth(day)
            air_mass_ratio = radiation.GetAirMassRatio(altitude_deg)
            # Reward is proportional to cosine distance between sun altitude and panel angle
            distBetweenSunAndPanel = abs(altitude_deg - panel_angle)
            actualSun = math.cos(math.radians(distBetweenSunAndPanel))
            return actualSun * flux * math.exp(-1 * optical_depth * air_mass_ratio)/100.
        else:
            return 0.0

    def _create_state(self, panel_angle, t):
        '''
        Args:
            sun_angle (int)
            panel_angle (int)

        Returns:
            (OOMDP State)
        '''

        self.objects = {attr : [] for attr in SolarOOMDP.CLASSES}

        # Make agent.
        agent_attributes = {}
        agent_attributes["angle"] = panel_angle
        agent = OOMDPObject(attributes=agent_attributes, name="agent")
        self.objects["agent"].append(agent)

        # Time.
        time_attributes = {}
        time_attributes["time"] = t.hour
        time = OOMDPObject(attributes=time_attributes, name="time")
        self.objects["time"].append(time)

        return SolarOOMDPState(self.objects)

    def _reward_func(self, state, action):
        '''
        Args:
            state (OOMDP State)
            action (str)

        Returns
            (float)
        '''
        altitude_deg = solar.GetAltitudeFast(self.latitude_deg, self.longitude_deg, self.time)
#        altitude_deg = solar.GetAltitude(self.latitude_deg, self.longitude_deg, d)
        reward = self._get_radiation(self.time, altitude_deg, state.get_panel_angle());

        # print 
        # print altitude_deg
        # print state.get_panel_angle()
        # print reward
        # print self.time
        # Add penalty for moving at all
        if ((action == 'panelForward') | (action == 'panelBack')):
            reward -= 0.05
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
        self.time += datetime.timedelta(minutes=self.timestep)
        time = self.time

        # If we move the panel forward, increment panel angle by one step
        if action == "panelForward":
            new_panel_angle = min(state.get_panel_angle() + self.step_panel, 180.0)
            return self._create_state(new_panel_angle, time)

        # If we move the panel back, decrement panel angle by one step
        elif action == "panelBack":
            new_panel_angle = max(state.get_panel_angle() - self.step_panel, 0.0)
            return self._create_state(new_panel_angle, time)

        # If we do nothing, none of the angles change
        elif action == "doNothing":
            return self._create_state(state.get_panel_angle(), time)
        else:
            print "Error: Unrecognized action! (" + action + ")"
            quit()
        
        
    def __str__(self):
        return "solarmdp_" + "p-" + str(self.step_panel)

def _error_check(state, action):
    '''
    Args:
        state (State)
        action (str)

    Summary:
        Checks to make sure the received state and action are of the right type.
    '''

    if action not in SolarOOMDP.ACTIONS:
        print "Error: the action provided (" + str(action) + ") was invalid."
        quit()

    if not isinstance(state, SolarOOMDPState):
        print "Error: the given state (" + str(state) + ") was not of the correct class."
        quit()

def main():
    agent = {"angle": 0}
    sun = {"angle": 0}
    solar_world = SolarOOMDP(0, 0, agent=agent, sun=sun)

if __name__ == "__main__":
    main()
