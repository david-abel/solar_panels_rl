import numpy as np

class Cloud(object):

    PIX_INTENSITY = .22

    def __init__(self, x, y, dx, dy, rx, ry, intensity=PIX_INTENSITY):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.rx, self.ry = rx, ry
        self.intensity = intensity

    def move(self, timestep):
        # Moves dx,dy every 20 minutes.
        self.x += self.dx * timestep/20.0
        self.y += self.dy * timestep/20.0

    def get_mu(self):
        return np.array([self.x, self.y])

    def get_sigma(self):
        return np.array([[self.rx, 0.2], [0.2, self.ry]])

    def get_intensity(self):
        return self.intensity

    def __str__(self):
        return "cloud: (x=" + str(self.x) + " y=" + str(self.y) + " rx=" + str(self.rx) + " ry=" + str(self.ry)