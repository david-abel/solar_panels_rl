'''
SolarOOMDPClass.py: Contains the SolarOOMDP class. 

Author: Emily Reif and David Abel
'''

# Python imports.
import math as m
import numpy as np
import datetime
import random
import matplotlib.pyplot as plt
import scipy.integrate as integrate

# simple_rl imports.
from simple_rl.mdp.oomdp.OOMDPClass import OOMDP
from simple_rl.mdp.oomdp.OOMDPObjectClass import OOMDPObject
from SolarOOMDPStateClass import SolarOOMDPState
from CloudClass import Cloud
import solar_helpers as sh

class SolarOOMDP(OOMDP):
    ''' Class for a Solar OO-MDP '''

    # Static constants.
    ACTIONS = ["panel_forward_ns", "panel_back_ns", "do_nothing", "panel_forward_ew", "panel_back_ew"]
    ATTRIBUTES = ["angle_AZ", "angle_ALT", "angle_ns", "angle_ew"]
    CLASSES = ["agent", "sun", "time", "worldPosition"]

    def __init__(self, date_time, timestep=30, panel_step=.1, reflective_index=0.8, panel_start_angle=0, latitude_deg=50, longitude_deg=1.1, img_dims=64, dual_axis=True, image_mode=False, cloud_mode=False):
        # Reykjavik, Iceland: latitude_deg=64.1265, longitude_deg=-21.8174
        # Mildura, Australia: latitude_deg=-34.25, longitude_deg=142.17

        # Error check the lat/long.
        if abs(latitude_deg) > 90 or abs(longitude_deg) > 180:
            print "Error: latitude must be between [-90, 90], longitude between [-180,180]. Lat:", latitude_deg, "Long:", longitude_deg
            quit()

        if cloud_mode and not image_mode:
            print "Warning (SolarOOMDP): Clouds were set to active but image mode is off. No cloud simulation supported for non-image-mode."
            cloud_mode = False

        # Mode information
        # If we are in 1-axis tracking mode, change actions accordingly.
        if not(dual_axis):
            SolarOOMDP.ACTIONS = ["do_nothing", "panel_forward_ew", "panel_back_ew"]

        # Image stuff.
        self.img_dims = 16
        self.image_mode = image_mode
        self.cloud_mode = cloud_mode
        self.clouds = self._generate_clouds() if cloud_mode else []

        # Global information
        self.latitude_deg = latitude_deg # positive in the northern hemisphere
        self.longitude_deg = longitude_deg # negative reckoning west from prime meridian in Greenwich, England
        self.step_panel = panel_step
        self.timestep = timestep
        self.reflective_index = 0.5

        # Time stuff.
        self.init_time = date_time
        self.time = date_time

        # Make state and call super.
        init_state = self._create_state(0.0, 0.0, self.init_time, longitude_deg, latitude_deg)
        OOMDP.__init__(self, SolarOOMDP.ACTIONS, self.objects, self._transition_func, self._reward_func, init_state=init_state)

    def reset(self):
        '''
        Summary:
            Resets the OOMDP back to the initial configuration.
        '''
        self.time = self.init_time
        OOMDP.reset(self)

    def _get_day(self):
        return self.time.timetuple().tm_yday

    # -------------------
    # --- CLOUD STUFF ---
    # -------------------

    def _generate_clouds(self):
        '''
        Returns:
            (list of Cloud)
        '''
        num_clouds = random.randint(4,8)
        clouds = []

        # Generate info for each cloud.
        dx, dy = random.randint(-1,1), random.randint(-1,1)
        for i in xrange(num_clouds):
            x = random.randint(0, self.img_dims)
            y = random.randint(0, self.img_dims)
            rx = random.randint(3,6)
            ry = random.randint(2,rx)
            clouds.append(Cloud(x, y, dx, dy, rx, ry))

        return clouds

    def _move_clouds(self):
        '''
        Summary:
            Moves each cloud in the cloud list (self.clouds).
        '''
        for cloud in self.clouds:
            cloud.move(self.timestep)

    # ----------------------------------
    # --- REWARD AND TRANSITION FUNC ---
    # ----------------------------------

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

        # Cloud stuff.
        direct_cloud_modifer = 1.0
        if self.cloud_mode:
            sun_x, sun_y = self._get_sun_x_y(sun_azimuth_deg, sun_altitude_deg)
            direct_cloud_modifer -= sh._compute_direct_cloud_cover(self.clouds, sun_x, sun_y, self.img_dims)

        # Compute direct radiation.
        direct_rads = sh._compute_radiation_direct(self.time, sun_altitude_deg)
        diffuse_rads = sh._compute_radiation_diffuse(self.time, self._get_day(), sun_altitude_deg)
        reflective_rads = sh._compute_radiation_reflective(self.time, self._get_day(), self.reflective_index, sun_altitude_deg)

        # Compute tilted component.
        direct_tilt_factor = sh._compute_direct_radiation_tilt_factor(panel_ns_deg, panel_ew_deg, sun_altitude_deg, sun_azimuth_deg)
        diffuse_tilt_factor = sh._compute_diffuse_radiation_tilt_factor(panel_ns_deg, panel_ew_deg)
        reflective_tilt_factor = sh._compute_reflective_radiation_tilt_factor(panel_ns_deg, panel_ew_deg)

        # Compute total.
        reward = direct_cloud_modifer*direct_rads * direct_tilt_factor + \
                    diffuse_rads * diffuse_tilt_factor + \
                    reflective_rads * reflective_tilt_factor

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
        state_angle_ns = state.get_panel_angle_ns()
        state_angle_ew = state.get_panel_angle_ew()

        # Remake or move clouds.
        if self.time.hour == 6:
            self.clouds = self._generate_clouds() if self.cloud_mode else []
        elif self.clouds != []:
            self._move_clouds()

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
        elif action == "do_nothing":
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
        bounded_panel_angle_ew = max(min(panel_angle_ew,90),-90)
        bounded_panel_angle_ns = max(min(panel_angle_ns,90),-90)
        agent_attributes["angle_ew"] = bounded_panel_angle_ew
        agent_attributes["angle_ns"] = bounded_panel_angle_ns

        agent = OOMDPObject(attributes=agent_attributes, name="agent")
        self.objects["agent"].append(agent)

        # Sun.
        sun_attributes = {}
        sun_angle_AZ = sh._compute_sun_azimuth(lat, lon, t)
        sun_angle_ALT = sh._compute_sun_altitude(lat, lon, t)

        # Image stuff.
        if (self.image_mode):
            # Set attributes as pixels.
            image = self._create_sun_image(sun_angle_AZ, sun_angle_ALT, bounded_panel_angle_ns, bounded_panel_angle_ew)
        # Image stuff.
        if self.image_mode:
            # Set attributes as pixels.
            image = self._create_sun_image(sun_angle_AZ, sun_angle_ALT)
            for i in range (self.img_dims):
                for j in range (self.img_dims):
                    idx = i*self.img_dims + j
                    sun_attributes['pix' + str(i)] = image[i][j]    
        else:
            sun_attributes["angle_AZ"] = sun_angle_AZ
            sun_attributes["angle_ALT"] = sun_angle_ALT  

        sun = OOMDPObject(attributes=sun_attributes, name="sun")
        self.objects["sun"].append(sun)

        return SolarOOMDPState(self.objects, date_time=t, longitude=lon, latitude=lat, sun_angle_AZ = sun_angle_AZ, sun_angle_ALT = sun_angle_ALT)
    
    # -------------------
    # --- IMAGE STUFF ---
    # -------------------

    def _get_sun_x_y(self, sun_angle_AZ, sun_angle_ALT):
        x = self.img_dims * (1 + m.sin(m.radians(sun_angle_AZ)))/2
        y = self.img_dims * m.sin(m.radians(sun_angle_ALT))/2
        return x, y

    def _create_sun_image(self, sun_angle_AZ, sun_angle_ALT, panel_angle_ns, panel_angle_ew):
        # Create image of the sun, given alt and az
        sun_dim = self.img_dims/8.0

        # For viewing purposes, we normalize between 0 and 1 on the x axis and 0 to .5 on the y axis
        panel_tilt_offset_y = m.sin(m.radians(panel_angle_ns))
        panel_tilt_offset_x = m.sin(m.radians(panel_angle_ew))

        print "sun az: ", sun_angle_AZ
        # print "sun alt: ", sun_angle_AZ

        percent_in_sky_x = m.sin(m.radians(sun_angle_AZ))
        percent_in_sky_y = m.sin(m.radians(sun_angle_ALT))

        print "panel_angle_ew ", panel_angle_ew
        x = self.img_dims * (1 + (percent_in_sky_x - panel_tilt_offset_x))/2 
        y = self.img_dims * (percent_in_sky_y - panel_tilt_offset_y)/2

        # image = [l[:] for l in [[0] * self.img_dims] * self.img_dims]
        image = [np.ones(self.img_dims)*0.8 for l in [[0] * self.img_dims] * self.img_dims]

        # Make gaussian sun
        for i in range (self.img_dims):
            for j in range (self.img_dims):
                image[i][j] += _gaussian(j, x, sun_dim) * _gaussian(i, y, sun_dim)

                # Add cloud cover.
                for cloud in self.clouds:
                    image[i][j] -= (_gaussian(j, cloud.get_mu()[0], cloud.get_sigma()[0][0]) * \
                                    _gaussian(i, cloud.get_mu()[1], cloud.get_sigma()[1][1]) * cloud.get_intensity())

                # Backcompute the altitude of the pixel; if it is below the horizon, render black.
                alt_pix = 2*float(i)/self.img_dims + panel_tilt_offset_y
                if alt_pix < 0:
                    image[i][j] = 1

        # Show image (for testing purposes)
        self._show_image(image)

        return image

    def _show_image(self, image):
        plt.imshow(image, cmap='gray', vmin=00.0, vmax=1.0, interpolation='nearest')
        plt.gca().invert_yaxis()
        plt.title( 'Images used to train model')
        plt.figtext(0.01, 0.95, 'Date and Time: ' + str(self.time.ctime()), fontsize = 11)
        plt.figtext(0.01, 0.9, 'Latitude: ' + str(self.latitude_deg), fontsize = 11)
        plt.figtext(0.01, 0.85, 'Longitude: ' + str(self.longitude_deg), fontsize = 11)
        plt.show()

    def __str__(self):
        percept = "true"
        if self.image_mode and self.cloud_mode:
            percept = "cloud_img"
        elif self.image_mode:
            percept = "img"
        return "solarmdp_" + "p-" + str(self.step_panel) + "_" + percept

# Credit to http://stackoverflow.com/questions/14873203/plotting-of-1-dimensional-gaussian-distribution-function
# TODO: fix ^
def _gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def _multivariate_gaussian(x, y, mu_vec, cov_matrix):
    '''
    Args;
        x (float)
        y (float)
        mu_vec (np.array)
        cov_matrix (np.matrix)

    Returns:
        (float): evaluates the PDF of the multivariate at the point x,y.
    '''
    numerator = np.exp(-.5 *np.transpose(np.array([x,y]) - mu_vec) * np.linalg.inv(cov_matrix) * (np.array([x,y]) - mu_vec))
    denominator = np.sqrt(np.linalg.det(2*m.pi*cov_matrix))

    res = numerator / denominator
    return res[0][0] + res[1][1]

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

# --- Test ---
def main():
    agent = {"angle": 0}
    sun = {"angle": 0}
    solar_world = SolarOOMDP(0, 0, agent=agent, sun=sun)

if __name__ == "__main__":
    main()
