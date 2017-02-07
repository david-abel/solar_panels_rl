'''
SolarOOMDPClass.py: Contains the SolarOOMDP class. 

Author: Emily Reif and David Abel
'''

# Python imports.
import math as m
import numpy
import datetime
import random
import scipy.integrate as integrate

# simple_rl imports.
from simple_rl.mdp.oomdp.OOMDPClass import OOMDP
from simple_rl.mdp.oomdp.OOMDPObjectClass import OOMDPObject
from SolarOOMDPStateClass import SolarOOMDPState
import solar_helpers as sh
import matplotlib.pyplot as plt

class SolarOOMDP(OOMDP):
    ''' Class for a Solar OO-MDP '''

    # Static constants.
    ACTIONS = ["panel_forward_ns", "panel_back_ns", "doNothing", "panel_forward_ew", "panel_back_ew"]
    ATTRIBUTES = ["angle_AZ", "angle_ALT", "angle_ns", "angle_ew"]
    CLASSES = ["agent", "sun", "time", "worldPosition"]

    def __init__(self, date_time, timestep=30, panel_step=.1, reflective_index=0.8, panel_start_angle=0, latitude_deg=50, longitude_deg=-20, img_dims = 16, dual_axis = True, image_mode = False):
        
        # Mode information
        # If we are in 1-axis tracking mode, change actions accordingly.


        # if we are in image mode, add pixels individually as attributes
        self.image_mode = image_mode

        # Global information
        self.latitude_deg = latitude_deg # positive in the northern hemisphere
        self.longitude_deg = longitude_deg # negative reckoning west from prime meridian in Greenwich, England
        self.step_panel = panel_step
        self.timestep = timestep
        self.reflective_index = reflective_index

        # Time stuff.
        self.init_time = date_time
        self.time = date_time

        # Image stuff.
        self.img_dims = img_dims

        # Make state and call super.
        init_state = self._create_state(0.0, -30.0, self.init_time, longitude_deg, latitude_deg)
        OOMDP.__init__(self, SolarOOMDP.ACTIONS, self.objects, self._transition_func, self._reward_func, init_state=init_state)

    def reset(self):
        self.time = self.init_time
        OOMDP.reset(self)

    def _get_day(self):
        return self.time.timetuple().tm_yday

    def _reward_func(self, state, action):
        '''
        Args:
            state (OOMDP State)
            action (str)

        Returns
            (float)
        '''

        # Both altitude_deg and azimuth_deg are in degrees.
        sun_altitude_deg = sh._compute_sun_altitude(self.latitude_deg, self.longitude_deg, self.time)
        sun_azimuth_deg = sh._compute_sun_azimuth(self.latitude_deg, self.longitude_deg, self.time)

        # Panel stuff
        panel_ns_deg = state.get_panel_angle_ew()
        panel_ew_deg = state.get_panel_angle_ns()

        # Compute direct radiation.
        direct_rads = sh._compute_radiation_direct(self.time, sun_altitude_deg)
        diffuse_rads = sh._compute_radiation_diffuse(self.time, self._get_day(), sun_altitude_deg)
        reflective_rads = sh._compute_radiation_reflective(self.time, self._get_day(), self.reflective_index, sun_altitude_deg)

        # Compute tilted component.
        direct_tilt_factor = sh._compute_direct_radiation_tilt_factor(panel_ns_deg, panel_ew_deg, sun_altitude_deg, sun_azimuth_deg)
        diffuse_tilt_factor = sh._compute_diffuse_radiation_tilt_factor(panel_ns_deg, panel_ew_deg)
        reflective_tilt_factor = sh._compute_reflective_radiation_tilt_factor(panel_ns_deg, panel_ew_deg)

        # Compute total.
        reward = direct_rads * direct_tilt_factor + \
                    diffuse_rads * diffuse_tilt_factor + \
                    reflective_rads * reflective_tilt_factor

        # Penalize for 
        if action != "doNothing":
            reward -= 10.0

        return reward


    def _sun_rads_to_tilted_panel_rads(self, rads_at_loc, sun_alt, sun_az, panel_ns, panel_ew):
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
        
        # Convert relevant params to radians.
        panel_az_radians = m.radians(panel_az)
        panel_alt_radians = m.radians(panel_alt)
        
        sun_alt_radians = m.radians(sun_alt)
        sun_az_radians = m.radians(sun_az)

        delta = m.radians(_compute_declination(self._get_day()))
        lat_radians = m.radians(self.latitude_deg)
        omega_s = numpy.arccos(-m.tan(lat_radians) * m.tan(delta))

        # This part is messed up.
        A, B = _compute_a_b(lat_radians, panel_az_radians, panel_alt_radians, delta)
        omega_rt, omega_st = _compute_omega_r_s(omega_s, A, B, panel_az_radians)
        tilt_ratio_numer = integrate.quad(lambda x: m.cos(panel_alt_radians * x), omega_rt, omega_st)
        tilt_ratio_denom = integrate.quad(lambda x: m.cos(sun_alt_radians * x), omega_s, omega_s + (omega_st - omega_rt))
        tilt_ratio = 0.0 if tilt_ratio_denom[0] == 0.0 else max(tilt_ratio_numer[0] / tilt_ratio_denom[0], 0.0)
        
        panel_rads = rads_at_loc * tilt_ratio

        return panel_rads

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
        state_angle_ns = state.get_panel_angle_ns()
        state_angle_ew = state.get_panel_angle_ew()

        step = self.step_panel

        # If we move the panel forward, increment panel angle by one step
        if action == "panel_forward_ew":
            new_panel_angle_ew = state_angle_ew + step
            return self._create_state(new_panel_angle_ew, state_angle_ns, self.time, self.longitude_deg, self.latitude_deg)

        # If we move the panel back, decrement panel angle by one step
        elif action == "panel_back_ew":
            new_panel_angle_ew = state_angle_ew - step
            return self._create_state(new_panel_angle_ew, state_angle_ns, self.time, self.longitude_deg, self.latitude_deg)

        # If we move the panel forward, increment panel angle by one step
        if action == "panel_forward_ns":
            new_panel_angle_ns = state_angle_ns + step
            return self._create_state(state_angle_ew, new_panel_angle_ns, self.time, self.longitude_deg, self.latitude_deg)

        # If we move the panel back, decrement panel angle by one step
        elif action == "panel_back_ns":
            new_panel_angle_ns = state_angle_ns - step
            return self._create_state(state_angle_ew, new_panel_angle_ns, self.time, self.longitude_deg, self.latitude_deg)

        # If we do nothing, none of the angles change
        elif action == "doNothing":
            return self._create_state(state_angle_ew, state_angle_ns, self.time, self.longitude_deg, self.latitude_deg)

        else:
            print "Error: Unrecognized action! (" + action + ")"
            quit()

    def _create_state(self, panel_angle_ew, panel_angle_ns, t, lon, lat):
        '''
        Args:
            sun_angle (int)
            panel_angle_ns (int)
            panel_angle_ew (int)
            t (datetime)
            lon (float)
            lat (float)

        Returns:
            (OOMDP State)
        '''
        self.objects = {attr : [] for attr in SolarOOMDP.CLASSES}

        # Make agent.
        agent_attributes = {}
        agent_attributes["angle_ns"] = max(min(panel_angle_ew,90),-90)
        agent_attributes["angle_ew"] = max(min(panel_angle_ns,90),-90)
        agent = OOMDPObject(attributes=agent_attributes, name="agent")
        self.objects["agent"].append(agent)

        # Sun.
        sun_attributes = {}
        sun_angle_AZ = sh._compute_sun_azimuth(lat, lon, t)
        sun_angle_ALT = sh._compute_sun_altitude(lat, lon, t)

        if (self.image_mode):
            image = self._create_sun_image(sun_angle_AZ, sun_angle_ALT)
            for i in range (self.img_dims):
                for j in range (self.img_dims):
                    idx = i*self.img_dims + j
                    sun_attributes['pix' + str(i)] = image[i][j]    

        # Add this stuff as another property in the state (like date_time, ect)
        else:
            sun_attributes["angle_ew"] = sun_angle_AZ
            sun_attributes["angle_ALT"] = sun_angle_ALT  

        sun = OOMDPObject(attributes=sun_attributes, name="sun")
        self.objects["sun"].append(sun)

        return SolarOOMDPState(self.objects, date_time=t, longitude=lon, latitude=lat, sun_angle_AZ = sun_angle_AZ, sun_angle_ALT = sun_angle_ALT)

    def _create_sun_image(self, sun_angle_AZ, sun_angle_ALT):
        # Create image of the sun, given alt and az
        sun_dim = self.img_dims/16

        # For viewing purposes, we normalize between 0 and 1 on the x axis and 0 to .5 on the y axis
        x = self.img_dims * (1 + m.sin(m.radians(sun_angle_AZ)))/2
        y = self.img_dims * m.sin(m.radians(sun_angle_ALT))/2
        image = [l[:] for l in [[0] * self.img_dims] * self.img_dims]

        # Make gaussian sun
        for i in range (self.img_dims):
            for j in range (self.img_dims):
                image[i][j] = self._gaussian(j, x, sun_dim) * self._gaussian(i, y, sun_dim)

        # Show image (for testing purposes)
        # self._show_image(image)

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
        return numpy.exp(-numpy.power(x - mu, 2.) / (2 * numpy.power(sig, 2.)))

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
