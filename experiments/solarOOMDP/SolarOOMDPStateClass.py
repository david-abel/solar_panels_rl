''' SolarOOMDPStateClass.py: Contains the SolarOOMDPState class. '''

# Local libs.
from simple_rl.mdp.oomdp.OOMDPStateClass import OOMDPState

class SolarOOMDPState(OOMDPState):
    ''' Class for Solar Panel States '''

    def __init__(self, objects, date_time, longitude, latitude, sun_angle_AZ, sun_angle_ALT, clouds=[]):
        self.date_time = date_time
        self.longitude = longitude
        self.latitude = latitude
        self.sun_angle_AZ = sun_angle_AZ
        self.sun_angle_ALT = sun_angle_ALT
        
        # Hm.
        self.clouds = clouds

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

    def get_date_time(self):
        return self.date_time

    # --- State Attributes ---

    def get_sun_angle_AZ(self):
        return self.sun_angle_AZ

    def get_sun_angle_ALT(self):
        return self.sun_angle_ALT

    def get_panel_angle_ew(self):
        return self.objects["agent"][0]["angle_ew"] * 1

    def get_panel_angle_ns(self):
        return self.objects["agent"][0]["angle_ns"] * 1