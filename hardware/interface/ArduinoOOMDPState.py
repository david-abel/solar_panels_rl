from simple_rl.mdp.oomdp.OOMDPStateClass import OOMDPState

class ArduinoOOMDPState(OOMDPState):
	'''
	Class for Arduino solar panel states.
	Contains the sun position, the current angle of the single-axis tracker,
	and the image recieved by the camera.
	The image and panel angles are represented as objects
	'''
	
	def __init__(self, objects, date_time, longitude, latitude, sun_angle_AZ, sun_angle_ALT):
		self.date_time = date_time
        self.longitude = longitude
        self.latitude = latitude
        self.sun_angle_AZ = sun_angle_AZ
        self.sun_angle_ALT = sun_angle_ALT
		
		
		OOMDPState.__init__(self, objects=objects)
