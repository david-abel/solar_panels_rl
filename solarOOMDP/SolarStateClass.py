''' SolarStateClass.py: Contains the SolarStateClass class. '''

# Local libs.
from ...mdp.StateClass import State

class SolarState(State):
    ''' Class for Solar MDP States '''

    def __init__(self, angle_sun, angle_panel):
        State.__init__(self, data=[angle_sun, angle_panel])
        self.angle_sun = int(angle_sun)
        self.angle_panel = int(angle_panel)

    def __hash__(self):
        return hash((int(self.angle_sun), int(self.angle_panel)))

    def __str__(self):
        return "s." + str(self.angle_sun) + "-" + str(self.angle_panel)

    def __eq__(self, other):
        '''
        Summary:
            Solar states are equal when their angles is the same
        '''
        return isinstance(other, SolarState) and (self.angle_sun == other.angle_sun) and (self.angle_panel == other.angle_panel) 
