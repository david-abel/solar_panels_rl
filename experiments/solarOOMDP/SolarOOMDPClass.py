'''
SolarOOMDPClass.py: Contains the SolarOOMDP class. 

Author: Emily Reif
'''

# simple_rl imports.
from simple_rl.mdp.oomdp.OOMDPClass import OOMDP
from simple_rl.mdp.oomdp.OOMDPObjectClass import OOMDPObject
from SolarOOMDPStateClass import SolarOOMDPState
import math
from Pysolar import solar, radiation
import datetime

class SolarOOMDP(OOMDP):
    ''' Class for a Solar OO-MDP '''

    # Static constants.
    ACTIONS = ["panelForwardAZ", "panelBackAZ", "panelForwardALT", "panelBackALT", "doNothing"]

    # give altitiude and azimuth
    ATTRIBUTES = ["angle_AZ", "angle_ALT", "month", "day", "hour", "minute", "latitude", "longitude"]
    CLASSES = ["agent", "time", "worldPosition"]

    #timestep is in minutes, for now
    def __init__(self, timestep=30, panel_step=.1, panel_start_angle=0, year=2016, month=11, day=4, hour=0, minute=0, latitude_deg = 42.3, longitude_deg = -71.4):
        self.time = datetime.datetime(year, month, day, hour, minute)
        init_state = self._create_state(0.0, 0.0, self.time, longitude_deg, latitude_deg)
        OOMDP.__init__(self, SolarOOMDP.ACTIONS, self.objects, self._transition_func, self._reward_func, init_state=init_state)

        # Global information
        self.latitude_deg = latitude_deg # positive in the northern hemisphere
        self.longitude_deg = longitude_deg # negative reckoning west from prime meridian in Greenwich, England
        self.step_panel = panel_step
        self.timestep = timestep

    def _reward_func(self, state, action):
        '''
        Args:
            state (OOMDP State)
            action (str)

        Returns
            (float)
        '''

        # Need to update altitude_deg to take into account our panel's rotation.
        # However, we can only control rotation over the ROT/UD axes.
        # So, decompose current altitude_deg into ROT/EW components using azimuth_deg.
        # Then, add panel offset, and translate back.

        # Both altitude_deg and azimuth_deg are in degrees.
        altitude_deg = solar.GetAltitudeFast(self.latitude_deg, self.longitude_deg, self.time)
        azimuth_deg = solar.GetAzimuth(self.latitude_deg, self.longitude_deg, self.time)

        # First, if the altitude is less than 0 (the sun is below the horizon), return 0.
        if (altitude_deg < 0):
            reward = 0.0
        else:
            # The panel has two rotation offsets (rotation around the normal to the ground), and rotation around its own axis.
            # Hopefully, it would learn to just make its normal rotation match that ground-truth azimuth angle,
            # and make its other rotation equal 90 - altitude_deg.

            # Translate to radians.
            azimuth_rad = math.cos(math.radians(azimuth_deg))

            # The difference between how we SHOULD have rotated the panel, and how we did.
            azimuth_panel_offset = azimuth_rad - state.get_panel_angle_AZ()

            # Finally, the new altitude is the ground's altitude with the addition of the panel's
            altitude_deg_with_panel = altitude_deg + math.degrees(state.get_panel_angle_ALT() * math.cos(azimuth_panel_offset))

            reward = GetRadiationDirect(self.time, altitude_deg_with_panel)/1000.0
            # print
            # print state.get_hour()
            # print "original altitude ", altitude_deg
            # print "panel angle az ", state.get_panel_angle_AZ()
            # print "panel angle alt ", state.get_panel_angle_ALT()
            # print "alt with panel ", altitude_deg_with_panel
            # print " REWARD ", reward

        if ((action != "doNothing")):
            reward -= .1
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
        state_angle_AZ = 0
        state_angle_AZ += state.get_panel_angle_AZ()
        state_angle_ALT = 0
        state_angle_ALT+= state.get_panel_angle_ALT()

        # If we move the panel forward, increment panel angle by one step
        if action == "panelForwardAZ":
            new_panel_angleAZ = state_angle_AZ + self.step_panel
            return self._create_state(new_panel_angleAZ, state_angle_ALT, time, self.longitude_deg, self.latitude_deg)

        # If we move the panel back, decrement panel angle by one step
        elif action == "panelBackAZ":
            new_panel_angleAZ = state_angle_AZ - self.step_panel
            return self._create_state(new_panel_angleAZ, state_angle_ALT, time, self.longitude_deg, self.latitude_deg)

        # If we move the panel forward, increment panel angle by one step
        if action == "panelForwardALT":
            new_panel_angle_ALT = state_angle_ALT + self.step_panel
            return self._create_state(state_angle_AZ, new_panel_angle_ALT, time, self.longitude_deg, self.latitude_deg)

        # If we move the panel back, decrement panel angle by one step
        elif action == "panelBackALT":
            new_panel_angle_ALT = state_angle_ALT - self.step_panel
            return self._create_state(state_angle_AZ, new_panel_angle_ALT, time, self.longitude_deg, self.latitude_deg)

        # If we do nothing, none of the angles change
        elif action == "doNothing":
            return self._create_state(state_angle_AZ, state_angle_ALT, time, self.longitude_deg, self.latitude_deg)

        else:
            print "Error: Unrecognized action! (" + action + ")"
            quit()

    def _create_state(self, panel_angle_AZ, panel_angle_ALT, t, lon, lat):
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
        agent_attributes["angle_AZ"] = panel_angle_AZ
        agent_attributes["angle_ALT"] = panel_angle_ALT
        agent = OOMDPObject(attributes=agent_attributes, name="agent")
        self.objects["agent"].append(agent)

        # Time.
        time_attributes = {}
        time_attributes["month"] = t.month
        time_attributes["day"] = t.day
        time_attributes["hour"] = t.hour
        time_attributes["minute"] = t.minute
        time = OOMDPObject(attributes=time_attributes, name="time")
        self.objects["time"].append(time)

        # Long/Lat
        pos_attributes = {}
        pos_attributes["longitude"] = lon
        pos_attributes["latitude"] = lat
        pos = OOMDPObject(attributes=pos_attributes, name="worldPosition")
        self.objects["worldPosition"].append(pos)

        return SolarOOMDPState(self.objects)

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


# DIRECTLY FROM PYSOLAR (with different conditional)
def GetRadiationDirect(utc_datetime, altitude_deg):
    # from Masters, p. 412
    if(altitude_deg > 5 and altitude_deg < 175):
        day = solar.GetDayOfYear(utc_datetime)
        flux = radiation.GetApparentExtraterrestrialFlux(day)
        optical_depth = radiation.GetOpticalDepth(day)
        air_mass_ratio = radiation.GetAirMassRatio(altitude_deg)
        return flux * math.exp(-1 * optical_depth * air_mass_ratio)
    else:
        return 0.0

def main():
    agent = {"angle": 0}
    sun = {"angle": 0}
    solar_world = SolarOOMDP(0, 0, agent=agent, sun=sun)

if __name__ == "__main__":
    main()
