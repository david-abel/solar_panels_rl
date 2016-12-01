''' SolarOOMDPStateClass.py: Contains the SolarOOMDPState class. '''

# Local libs.
from simple_rl.mdp.oomdp.OOMDPStateClass import OOMDPState

class SolarOOMDPState(OOMDPState):
    ''' Class for Taxi World States '''

    def __init__(self, objects):
        OOMDPState.__init__(self, objects=objects)

    def get_month(self):
        return self.objects["time"][0]["month"] * 1

    def get_day(self):
        return self.objects["time"][0]["day"] * 1

    def get_hour(self):
        return self.objects["time"][0]["hour"] * 1

    def get_minute(self):
        return self.objects["time"][0]["minute"] * 1

    def get_panel_angle_NS(self):
        return self.objects["agent"][0]["angle_NS"] * 1

    def get_panel_angle_EW(self):
        return self.objects["agent"][0]["angle_EW"] * 1