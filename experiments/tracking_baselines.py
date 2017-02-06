'''
tracking_baselines.py

Contains tracking functions for computing the location of the sun, primarily from:

	"Five new algorithms for the computation of sun position from 2010 to 2110"
	by Roberto Grena, 2012, Solar Energy, Volume 86.
'''

# Python libs.
import math as m
import numpy

def _compute_new_times(year, month, day, hour):
	'''
	Args:
		Same as algorithms below

	Returns:
		(tuple):
			year (int)
			month (int)
			time (int)
			rotation_independent_time (int)
	'''
	# From Grena
	if month <= 2:
		month += 12
		year -= 1
	time = int(365.25 * (year - 2000)) + int(30.6001 * (month + 1)) \
		- int(0.01 * year) + day + 0.0416667* hour - 21958
	
	delta_t = 96.4 + 0.00158 * time

	rot_ind_time = time + 1.1574 * 10**(-5) * delta_t

	return year, month, time, rot_ind_time

def static_policy(state, action="doNothing"):
	return action

# ==========================
# ======== TRACKERS ========
# ==========================

def tracker_from_state_info(state):
	'''
	Args:
		state (SolarOOMDP state): contains the panel and sun az/alt.
		panel_shift (int): how much to move the panel by each timestep.

	Returns:
		(tuple): <sun_az, sun_alt>
	'''

	# When state has this stuff.
	sun_az = state.get_sun_angle_AZ()
	sun_alt = state.get_sun_angle_ALT()

	return sun_az, sun_alt

def tracker_from_day_time_loc(state, tracker):
	'''
	Args:
		state (SolarOOMDP state): contains the year, month, hour etc.

	Returns:
		(tuple): <sun_az, sun_alt>
	'''

	# Get relevant data.
	year, month, hour, day, = state.get_year(), state.get_month(), state.get_hour(), state.get_day()
	longitude, latitude = state.get_longitude(), state.get_latitude()

	# Use tracker to compute sun vector.
	sun_az, sun_alt = tracker(year, month, hour, day, delta_t, longitude, latitude)

	return sun_az, sun_alt

def grena_tracker(year, month, hour, day, delta_t, longitude, latitude):
	pass

def simple_tracker(state, simple=True):
	'''
	Args:
		state (OOMDPstate)
		simple (boolean): If true, uses Algorithm One from [Grena 2012], else uses Algorithm two

	Returns:
		(5-tuple):
			right_ascension: "azimuthal angle measured from the ascending point"
			declination: polar coordinates relative to earth's rotation
			hour_angle: "the azimuthal angle of the sun with the polar axis aligned with the earth axis"
			zenith:
			azimuth:
	'''
	year, month, day, hour = state.get_year(), state.get_month(), state.get_day(), state.get_hour()
	latitude, longitude = state.get_latitude(), state.get_longitude()
	year, month, time, rot_ind_time = _compute_new_times(year, month, day, hour)

	angular_freq = 0.017202786 * day**(-1)

	# Global Coordinate: Alpha
	right_asc = -1.3888 + 1.7202792 * 10**(-2)*rot_ind_time \
		+ 3.199 * 10**(-2) * m.sin(angular_freq * rot_ind_time) \
		- 2.65 * 10**(-3) * m.cos(angular_freq * rot_ind_time) \
		+ 4.050 * 10**(-2) * m.sin(2 * angular_freq * rot_ind_time) \
		+ 1.525 * 10**(-2) * m.cos(2 * angular_freq * rot_ind_time)

	# Global Coordinate: Delta
	declination = 6.57 * 10**(-3) + 7.347 * 10**(-2) * m.sin(angular_freq * rot_ind_time) \
	 	-3.9919 * 10**(-1) * m.cos(angular_freq * rot_ind_time) + 7.3 * 10 ** (-4) * m.sin(2 * angular_freq * rot_ind_time) \
	 	- 6.60 * 10**(-3) * m.cos(2 * angular_freq * rot_ind_time)

	# Local Coordinate: H
	hour_angle = 1.75283 + 6.3003881 * time + longitude - right_asc

	# Mod stuff.
	right_asc = right_asc % 2 * m.pi
	hour_angle = ((hour_angle + m.pi) % 2 * m.pi) - m.pi

	altitude_deg, azimuth_deg = _asc_decl_ha_to_alt_az(right_asc, declination, hour_angle, latitude)

	# When state has this stuff.
	sun_az = state.get_sun_angle_AZ()
	sun_alt = state.get_sun_angle_ALT()
	print "sun, estimate", sun_az, sun_alt, azimuth_deg, altitude_deg

	return right_asc, hour_angle

def _asc_decl_ha_to_alt_az(right_asc, declination, hour_angle, latitude):
	latitude_radians = m.radians(latitude)
	alt_temp = m.sin(declination)*m.sin(latitude_radians)+m.cos(declination)*m.cos(latitude_radians)*m.cos(hour_angle)
	altitude = numpy.arcsin(alt_temp)

	az_temp = (m.sin(declination) - m.sin(altitude) * m.sin(latitude_radians)) / (m.cos(altitude)*m.cos(latitude_radians))
	azimuth = numpy.arccos(az_temp)
	if m.sin(hour_angle) >= 0:
		azimuth = 360 - azimuth

	return m.degrees(altitude), m.degrees(azimuth)

def main():
	simple_tracker(year=2060, month=1, hour=13, day=26, delta_t=0, longitude=.1, latitude=-.2)

if __name__ == "__main__":
	main()