#class for interfacing with arduino agent.

import serial

class ArduinoAgent:
    def __init__(self, serial_loc='/dev/tty.usbserial', baud=9600, verbose=True):
        '''
        Initializes the agent and opens a serial port.
        '''

        print "initializing agent at location {} with baud {}".format(serial_loc, baud)

    def get_panel_readout(self):
        '''
        Gets the current, voltage, and power from the panel.
        '''
        if verbose:
            print "requesting panel power stats"

    def move(self, direction):
        '''
        Requests a move action in the given direction. Returns the power consumed during that action.
        '''

        if verbose:
            print "requesting move in direction {}".format(direction)
