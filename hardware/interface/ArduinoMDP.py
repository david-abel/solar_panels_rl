from simple_rl.mdp.MDPClass import MDP

#arduino MDP class

#based off Gym MDP class
class ArduinoMDP(MDP):
    def __init__(self, serial_loc='/dev/tty.usbserial', baud=9600, verbose=True):
        '''
        Initializes connection to arduino + camera.
        '''

    def _reward_func(self, state, action):
        '''
        Takes an action in the current state:
        Sends command to arduino
        Once command is sent, wait until reward is receieved from arduino
        Get new state (camera image), set next state
        Returns reward value
        '''




    def _transition_func(self, state, action):
        '''
        Returns next state returned from camera
        '''

        return self._next_state
