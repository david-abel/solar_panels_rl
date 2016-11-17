''' SolarOOMDPStateClass.py: Contains the SolarOOMDPState class. '''

# Local libs.
from ...mdp.oomdp.OOMDPStateClass import OOMDPState

class SolarOOMDPState(OOMDPState):
    ''' Class for Taxi World States '''

    def __init__(self, objects):
        OOMDPState.__init__(self, objects=objects)

    def get_sun_angle(self):
        return self.objects["sun"][0]["angle"]

    def get_panel_angle(self):
        return self.objects["agent"][0]["angle"]