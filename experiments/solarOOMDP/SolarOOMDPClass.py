'''
SolarOOMDPClass.py: Contains the SolarOOMDP class. 

Author: Emily Reif
'''

# simple_rl imports.
from simple_rl.mdp.oomdp.OOMDPClass import OOMDP
from simple_rl.mdp.oomdp.OOMDPObjectClass import OOMDPObject
from SolarOOMDPStateClass import SolarOOMDPState
<<<<<<< HEAD
import math as m
import numpy
from pysolar import solar, radiation
import datetime
import random
=======
import math
from Pysolar import solar, radiation
import datetime
import numpy as np
from matplotlib import pyplot as plt
>>>>>>> a4b8f356d1e12a15ef684d184eb4b385f66f4e04

class SolarOOMDP(OOMDP):
    ''' Class for a Solar OO-MDP '''

    # Static constants.
    ACTIONS = ["panelForwardALT", "panelBackALT", "doNothing"] # "panelForwardAZ", "panelBackAZ", 

    # give altitiude and azimuth
    ATTRIBUTES = ["angle_AZ", "angle_ALT", "month", "day", "hour", "minute", "latitude", "longitude"]


    CLASSES = ["agent", "sun", "time", "worldPosition"]

    #timestep is in minutes, for now
<<<<<<< HEAD
    def __init__(self, timestep=30, panel_step=.1, panel_start_angle=0, year=2016, month=11, day=4, hour=0, minute=0, latitude_deg = 20, longitude_deg = 20):
        self.time = datetime.datetime(year, month, day, hour, minute)
        self.day = day
        init_state = self._create_state(90.0, 90.0, self.time, longitude_deg, latitude_deg)
        OOMDP.__init__(self, SolarOOMDP.ACTIONS, self.objects, self._transition_func, self._reward_func, init_state=init_state)

=======
    def __init__(self, timestep=30, panel_step=.1, panel_start_angle=0, year=2016, month=11, day=4, hour=0, minute=0, latitude_deg = 51.5074, longitude_deg = 0.1278, img_dims = 64):
>>>>>>> a4b8f356d1e12a15ef684d184eb4b385f66f4e04
        # Global information
        self.latitude_deg = latitude_deg # positive in the northern hemisphere
        self.longitude_deg = longitude_deg # negative reckoning west from prime meridian in Greenwich, England
        self.step_panel = panel_step
        self.timestep = timestep
        self.time = datetime.datetime(year, month, day, hour, minute)
        self.img_dims = img_dims


        init_state = self._create_state(90.0, 90.0, self.time, longitude_deg, latitude_deg)
        OOMDP.__init__(self, SolarOOMDP.ACTIONS, self.objects, self._transition_func, self._reward_func, init_state=init_state)



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
        sun_altitude_deg = solar.GetAltitudeFast(self.latitude_deg, self.longitude_deg, self.time)
        sun_azimuth_deg = solar.GetAzimuth(self.latitude_deg, self.longitude_deg, self.time)

        rads = 0.0
        # First, if the altitude is less than 0 (the sun is below the horizon), return 0.
        if sun_altitude_deg > 0:
            # The panel has two rotation offsets (rotation around the normal to the ground), and rotation around its own axis.
            # Hopefully, it would learn to just make its normal rotation match that ground-truth azimuth angle,
            # and make its other rotation equal 90 - altitude_deg.

            # The difference between how we SHOULD have rotated the panel, and how we did.
            # azimuth_panel_offset_rads = m.radians(sun_azimuth_deg - state.get_panel_angle_AZ())

            # Finally, the new altitude is the ground's altitude with the addition of the panel's
            # altitude_deg_with_panel = sun_altitude_deg + state.get_panel_angle_ALT() * m.cos(azimuth_panel_offset_rads)

            # Compute energy.
            rads += _get_radiation_direct(self.time, sun_altitude_deg)

        reward = self._sun_rads_to_tilted_panel_rads(rads, state.get_panel_angle_ALT()) / 1000.0

        if action != "doNothing":
            reward -= 0.1

        return reward

    def _compute_declination(self):
        term_one = (23.45 * m.pi) / 180
        term_two = m.sin( (2*m.pi*(284 + self.day)) / 365)
        return term_two * term_two


    def _sun_rads_to_tilted_panel_rads(self, rads_at_loc, panel_alt):
        '''
        Args:
            rads_at_loc (float)
            panel_alt (float in [0, 180])
            panel_az (float in [0, 180])
            delta (declination): Computed via Equation (2) of 
                Benghanem, M. "Optimization of tilt angle for solar panel: Case study for Madinah, Saudi Arabia."
                Applied Energy 88.4 (2011): 1427-1433.

        Summary:
            Computes the tilt coefficient for solar irradiance, from:
                Andersen P (1980) Comments on "Calculation of monthly average insolation on tilted surfaces" by SA Klein.
                Solar Energy: 25.
        '''
        delta = self._compute_declination()
        latitude = self.latitude_deg
        omega_ss = numpy.arccos(-m.tan(m.radians(latitude)) * m.tan(delta))

        # Compute tilt ratio N/S.
        tilt_ratio_numerator = m.cos(latitude - panel_alt) * m.cos(delta) * m.sin(omega_ss) + omega_ss * m.sin(latitude - panel_alt) * m.sin(delta)
        tilt_ratio_denominator = m.cos(latitude) * m.cos(delta) * m.sin(omega_ss) + omega_ss * m.sin(latitude) * m.sin(delta)
        tilt_ratio_ns = max((tilt_ratio_numerator / tilt_ratio_denominator), 0)

        # tilt_ratio_numerator = m.cos(latitude - panel_alt) * m.cos(delta) * m.sin(omega_ss) + omega_ss * m.sin(latitude - panel_alt) * m.sin(delta)
        # tilt_ratio_denominator = m.cos(latitude) * m.cos(delta) * m.sin(omega_ss) + omega_ss * m.sin(latitude) * m.sin(delta)


        panel_rads = rads_at_loc * tilt_ratio_ns

        return panel_rads

    def _transition_func(self, state, action):
        '''
        Args:
            (OOMDP State)
            action (str)

        Returns
            (OOMDP State)
        '''
        # print "s", state

        _error_check(state, action)
        self.time += datetime.timedelta(minutes=self.timestep)
        time = self.time
        state_angle_AZ = state.get_panel_angle_AZ()
        state_angle_ALT = state.get_panel_angle_ALT()

        step = random.randint(self.step_panel - 1, self.step_panel + 1)

        # If we move the panel forward, increment panel angle by one step
        if action == "panelForwardAZ":
            new_panel_angleAZ = state_angle_AZ + step
            return self._create_state(new_panel_angleAZ, state_angle_ALT, time, self.longitude_deg, self.latitude_deg)

        # If we move the panel back, decrement panel angle by one step
        elif action == "panelBackAZ":
            new_panel_angleAZ = state_angle_AZ - step
            return self._create_state(new_panel_angleAZ, state_angle_ALT, time, self.longitude_deg, self.latitude_deg)

        # If we move the panel forward, increment panel angle by one step
        if action == "panelForwardALT":
            new_panel_angle_ALT = state_angle_ALT + step
            return self._create_state(state_angle_AZ, new_panel_angle_ALT, time, self.longitude_deg, self.latitude_deg)

        # If we move the panel back, decrement panel angle by one step
        elif action == "panelBackALT":
            new_panel_angle_ALT = state_angle_ALT - step
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
            panel_angle_AZ (int)
            panel_angle_ALT (int)

        Returns:
            (OOMDP State)
        '''
        self.objects = {attr : [] for attr in SolarOOMDP.CLASSES}

        # Make agent.
        agent_attributes = {}
        agent_attributes["angle_AZ"] = max(min(panel_angle_AZ,180),0)
        agent_attributes["angle_ALT"] = max(min(panel_angle_ALT,180),0)
        agent = OOMDPObject(attributes=agent_attributes, name="agent")
        self.objects["agent"].append(agent)

        # Sun.
        sun_attributes = {}
        sun_angle_AZ = solar.GetAzimuth(lat, lon, t)
        sun_angle_ALT = solar.GetAltitudeFast(lat, lon, t)
        # sun_attributes["angle_AZ"] = sun_angle_AZ
        # sun_attributes["angle_ALT"] = sun_angle_ALT
        image = self._create_sun_image(sun_angle_AZ, sun_angle_ALT)
        for i in range (self.img_dims):
            for j in range (self.img_dims):
                idx = i*self.img_dims + j
                sun_attributes['pix' + str(i)] = image[i][j]

        sun = OOMDPObject(attributes=sun_attributes, name="sun")
        self.objects["sun"].append(sun)

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

    def _create_sun_image(self, sun_angle_AZ, sun_angle_ALT):
        # Create image of the sun, given alt and az
        sun_dim = self.img_dims/16

        # For viewing purposes, we normalize between 0 and 1 on the x axis and 0 to .5 on the y axis
        x = self.img_dims * (1 + math.sin(math.radians(sun_angle_AZ)))/2
        y = self.img_dims * math.sin(math.radians(sun_angle_ALT))/2
        image = [l[:] for l in [[0] * self.img_dims] * self.img_dims]

        # Make gaussian sun
        for i in range (self.img_dims):
            for j in range (self.img_dims):
                image[i][j] = self._gaussian(j, x, sun_dim) * self._gaussian(i, y, sun_dim)

        # Show image (for testing purposes)
        self._show_image(image)

        return image

    def _show_image(self, image):
        plt.imshow(image, cmap='Greys', interpolation='nearest')
        plt.gca().invert_yaxis()
        plt.title( 'Images used to train model')
        plt.figtext(0.01, 0.95, 'Date and Time: ' + str(self.time.ctime()), fontsize = 11)
        plt.figtext(0.01, 0.9, 'Latitude: ' + str(self.latitude_deg), fontsize = 11)
        plt.figtext(0.01, 0.85, 'Longitude: ' + str(self.longitude_deg), fontsize = 11)
        plt.show()

    # Credit to http://stackoverflow.com/questions/14873203/plotting-of-1-dimensional-gaussian-distribution-function
    # TODO: fix ^
    def _gaussian(self, x, mu, sig):
        return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

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
def _get_radiation_direct(utc_datetime, altitude_deg):
    # from Masters, p. 412
    if 5 < altitude_deg < 175:
        day = solar.GetDayOfYear(utc_datetime)
        flux = radiation.GetApparentExtraterrestrialFlux(day)
        optical_depth = radiation.GetOpticalDepth(day)
        air_mass_ratio = radiation.GetAirMassRatio(altitude_deg)
        return flux * m.exp(-1 * optical_depth * air_mass_ratio)
    else:
        return 0.0

def main():
    agent = {"angle": 0}
    sun = {"angle": 0}
    solar_world = SolarOOMDP(0, 0, agent=agent, sun=sun)

if __name__ == "__main__":
    main()
