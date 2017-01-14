'''
tracking_baselines.py

Contains several baselines for tracking the location of the sun from:

	"Five new algorithms for the computation of sun position from 2010 to 2110"
	by Roberto Grena, 2012, Solar Energy, Volume 86.
'''

# Python libs.
import math

def _compute_new_times(year, month, day, hour, delta_t):
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

	rot_ind_time = time + 1.1574 * 10**(-5) * delta_t

	return year, month, time, rot_ind_time

def static_policy(state):
	return "doNothing"


def policy_from_tracker(state, tracker):
	'''
	Args:
		state (SolarOOMDP state): contains the year, month, hour etc.
		tracker (lambda: {year, time ...} --> azimuth, altitude)

	Returns:
		(str): Action in the set SolarOOMDPClass.ACTIONS
	'''

	# Get relevant data.
	year, month, hour, day, = state.get_year(), state.get_month(), state.get_hour(), state.get_day()
	delta_t, longitude, latitude = state.get_delta_t(), state.get_longitude(), state.get_latitude()

	# Use tracker to compute sun vector.
	azimuth, altitude = tracker(year, month, hour, day, delta_t, longitude, latitude)
	sun_vector = math.sin(azimuth), math.cos(azimuth), math.sin(altitude)

	# Compute difference between panel vector and sun vector
	panel_vector = math.sin(math.radians(state.get_panel_angle_NS)), math.cos(math.radians(state.get_panel_angle_NS)), math.cos(math.radians(state.get_panel_angle_EW()))

	biggest_diff = 0
	biggest_index = 0
	for i in range(len(sun_vector)):
		delta = abs(sun_vector[i] - panel_vector[i])
		if delta > biggest_diff:
			biggest_index = i
			biggest_diff = delta

	# This will be more sophisticated.
	if biggest_diff <= 5:
		return "doNothing"
	elif biggest_index == 0 and sun_vector[0] - panel_vector[0] > 0:
		return "panelForwardNS"
	elif biggest_index == 0 and panel_vector[0] - sun_vector[0] >= 0:
		return "panelBackNS"
	else:
		return "panelForward"


["panelForwardNS", "panelBackNS", "panelForwardEW", "panelBackEW", "doNothing"]

def grena_tracker(year, month, hour, day, delta_t, longitude, latitude):
	pass

def simple_tracker(year, month, hour, day, delta_t, longitude, latitude):
	'''
	Args:
		year (int)
		month (int)
		hour (int)
		delta_t (int): Difference between Terrestrial Time and Universal Time
		longitude (float): WGS84
		latitude (float): WGS84

	Notes:
		Algorithm One from [Grena 2012].

	Returns:
		(5-tuple):
			right_ascension: "azimuthal angle measured from the ascending point"
			declination: polar coordinates relative to earth's rotation
			hour_angle: "the azimuthal angle of the sun with the polar axis aligned with the earth axis"
			zenith:
			azimuth:
	'''
	year, month, time, rot_ind_time = _compute_new_times(year, month, day, hour, delta_t)

	angular_freq = 0.017202786 * day**(-1)

	# Global Coordinate: Alpha
	right_asc = -1.3888 + 1.7202792 * 10**(-2)*rot_ind_time \
		+ 3.199 * 10**(-2) * math.sin(angular_freq * rot_ind_time) \
		- 2.65 * 10**(-3) * math.cos(angular_freq * rot_ind_time) \
		+ 4.050 * 10**(-2) * math.sin(2 * angular_freq * rot_ind_time) \
		+ 1.525 * 10**(-2) * math.cos(2 * angular_freq * rot_ind_time)

	# Global Coordinate: Delta
	declination = 6.57 * 10**(-3) + 7.347 * 10**(-2) * math.sin(angular_freq * rot_ind_time) \
	 	-3.9919 * 10**(-1) * math.cos(angular_freq * rot_ind_time) + 7.3 * 10 ** (-4) * math.sin(2 * angular_freq * rot_ind_time) \
	 	- 6.60 * 10**(-3) * math.cos(2 * angular_freq * rot_ind_time)

	# Local Coordinate: H
	hour_angle = 1.75283 + 6.3003881 * time + longitude - right_asc

	return right_asc, declination, hour_angle

def bad_tracker(year, month, hour, day, delta_t, longitude, latitude):
	return 0.0, 0.0


def main():
	simple_tracker(year=2060, month=1, hour=13, day=26, delta_t=0, longitude=.1, latitude=-.2)

if __name__ == "__main__":
	main()