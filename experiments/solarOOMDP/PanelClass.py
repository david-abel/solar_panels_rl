#class storing parameters for dual-axis panel setup, using linear actuators to rotate along axes.

import numpy as np

g = 9.8 #meters per second

class Panel():
    def __init__(self,
                    x_dim,
                    y_dim,
                    assembly_mass, #total mass of panel assembly, panel + mount
                    COM_offset, #offset between center of mass and radial axis
                    bearing_friction, #friction on bearing, assuming constant?
                    efficiency,
                    offset_angle,
                    actuator_force,
                    actuator_offset_ew,
                    actuator_mount_ew,
                    actuator_offset_ns,
                    actuator_mount_ns):
        '''
        :param x_dim: length of panel (meters)
        :param y_dim: width of panel (meters)
        :param mass: panel mass (kg)
        :param efficiency: energy conversion efficiency of solar panel (pct)
        :param actuator_force: force exerted by actuator (assumed to be constant) (Newtons)
        :param actuator_offset_1: distance between panel center and actuator mount across axis 1 (m)
        :param actuator_mount_1: length of actuator mount arm for axis 1. (m)
        :param actuator_offset_2: distance between panel center and actuator mount across axis 2 (m)
        :param actuator_mount_2: length of actuator mount arm for axis 2. (m)
        '''
        self.x_dim, self.y_dim = x_dim, y_dim
        self.mass = assembly_mass
        self.efficiency = efficiency
        self.COM_offset = COM_offset
        self.offset_angle = offset_angle
        self.bearing_friction = bearing_friction #TODO: implement this

        #actuator specs
        #self.actuator_force = actuator_force

        #dictionary of actuator mount attributes
        self.actuator_attrib = {}

        self.actuator_attrib['ew'] = {'offset': actuator_offset_ew, 'mount':actuator_mount_ew}
        self.actuator_attrib['ns'] = {'offset': actuator_offset_ns, 'mount': actuator_mount_ns}


    def get_power(self, flux):
        '''
        Returns the electrical power output in Watts of panel with the given flux
        :param flux: input flux of solar panel (W)
        :return: electrical power of solar panel (W)
        '''
        return self.x_dim*self.y_dim*self.efficiency*flux

    def __get_load__(self, axis, current_angle):
        '''
        Returns the load on the actuator for the current angle.
        Very simple, ignoring friction for now.
        :return:
        '''

        #TODO: model friction

        #calculate torque due to gravity:

        #torque = COM_offset*mass*g_sin \theta
        torque_g = self.COM_offset*self.mass*g*np.sin(current_angle)

        # print "current angle: {} torque: {}".format(current_angle, torque_g)

        #assume gravitational torque is equal to load, i.e. moving at constant velocity

        #calculate torque offset angle, a function of the current panel config and a constant param of the panel design

        l = self.__get_actuator_length__(axis, current_angle)

        mount = self.actuator_attrib[axis]['mount']
        offset = self.actuator_attrib[axis]['offset']

        #law of cosines: mount^2 = l^2 + offset^2 - 2*l*offset*cos(\phi)

        #angle between mount and actuator
        offset_angle_1 = np.arccos((np.square(mount) - np.square(l) - np.square(offset))/(-2*l*offset))

        total_offset = offset_angle_1 + self.offset_angle

        f_actuator = torque_g/np.sin(total_offset)

        return f_actuator

    def __get_actuator_length__(self, axis, current_angle):
        '''
        Computes the current length of the actuator.
        :param axis: axis indicator
        :param current_angle: current angle of panel for this axis
        :return:
        '''

        #x^2 = a^2 + b^2 - 2abcos(\theta)
        a = self.actuator_attrib[axis]['mount']
        b = self.actuator_attrib[axis]['offset']

        return np.sqrt(np.square(a) + np.square(b) - 2 * a * b * np.cos(current_angle))

    def get_rotation_energy_for_axis(self, axis, current_angle, delta_theta, actuator_efficiency=1.):
        '''
        :param current_angle: the current angle of the panel for this axis (radians)
        :param delta_theta: angle change (radians)
        :param axis: axis indicator (ew or ns)
        :return: energy consumed during rotation operation (Joules)
        '''

        #TODO: model linear actuator efficiency - assuming right now 100% electrical/physical work conversion

        # compute dx
        # (distance extended by linear actuator as a function of current_angle, delta_theta and the panel configuration)

        a = self.actuator_attrib[axis]['mount']
        b = self.actuator_attrib[axis]['offset']

        #computing f(\theta) = x with law of cosines: x^2 = a^2 + b^2 - 2abcos(\theta)

        dx = (a*b*np.sin(current_angle))/np.sqrt(np.square(a) + np.square(b) - 2*a*b*np.cos(current_angle))*delta_theta

        #W = F*dx (Joules)

        #absolute value - delta theta is always positive even when moving backwards

        force = self.__get_load__(axis, current_angle)

        #assumption = friction ~= load*coeff

        force_total = force + self.bearing_friction*force

        work = np.abs(force_total*dx/actuator_efficiency)
        #print "force: {}, work: {}".format(force, work)

        return work






