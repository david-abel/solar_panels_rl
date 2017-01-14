import math

def vec_from_azim_alt(azimuth, altitude):
	'''
	Args:
		azimuth (float): radians
		altitude (float): radians

	Returns:
		list: [x,y,z]
	'''
	return [math.cos(azimuth), math.sin(azimuth), math.sin(math.radians(altitude))] 