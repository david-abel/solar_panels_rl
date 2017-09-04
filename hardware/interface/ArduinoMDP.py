from simple_rl.mdp.MDPClass import MDP
import serial
import time
from SimpleCV import Camera

#based off Gym MDP class
class ArduinoMDP(MDP):
    def __init__(self, serial_loc='/dev/ttyACM0', baud=9600, verbose=True):
        '''
        Initializes connection to arduino + camera.
        '''
        
        self.cam = Camera(1)
        time.sleep(0.1)  # If you don't wait, the image will be dark
        self.ser = serial.Serial(serial_loc, baud)
		self.ser.write("INIT")
		result = ser.readline()
		if result == "RECV":
			print "connection established"        
        

    def _reward_func(self, state, action):
        '''
        Takes an action in the current state:
        Sends command to arduino
        Once command is sent, wait until reward is receieved from arduino
        Get new state (camera image), set next state
        Returns reward value
        '''
        
        #send action to arduino
		ser.write(action)
		
		reward = float(serial.readline())

		#next_state is camera image
		
		self._next_state = cam.getImage()
        
		return reward

    def _transition_func(self, state, action):
        '''
        Returns next state returned from camera
        '''
        return self._next_state

'''

Testing class 
'''
if __name__=="__main__":
	mdp_test = ArduinoMDP()
	
	
