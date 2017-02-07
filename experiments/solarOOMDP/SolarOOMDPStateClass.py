''' SolarOOMDPStateClass.py: Contains the SolarOOMDPState class. '''

# Local libs.
from simple_rl.mdp.oomdp.OOMDPStateClass import OOMDPState

class SolarOOMDPState(OOMDPState):
    ''' Class for Solar Panel States '''

    def __init__(self, objects, date_time, longitude, latitude):
        self.date_time = date_time
        self.longitude = longitude
        self.latitude = latitude
        OOMDPState.__init__(self, objects=objects)


    # --- Time and Loc (for trackers) ---

    def get_day_of_year(self):
        return self.date_time.timetuple().tm_yday

    def get_year(self):
        return self.date_time.year

    def get_month(self):
        return self.date_time.month

    def get_day(self):
        return self.date_time.day

    def get_hour(self):
        return self.date_time.hour

    def get_longitude(self):
        return self.longitude

    def get_latitude(self):
        return self.latitude

    # --- State Attributes ---

    def get_sun_angle_AZ(self):
        return self.objects["sun"][0]["angle_AZ"] * 1

    def get_sun_angle_ALT(self):
        return self.objects["sun"][0]["angle_ALT"] * 1

    def get_panel_angle_AZ(self):
        return self.objects["agent"][0]["angle_AZ"] * 1

    def get_panel_angle_ALT(self):
        return self.objects["agent"][0]["angle_ALT"] * 1