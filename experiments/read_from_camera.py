# Imports.
import time
from SimpleCV import Camera

cam = Camera(1) # Reads "2nd" camera (not webcam, looks for USB).
time.sleep(0.1)  # If you don't wait, the image will be dark
img = cam.getImage()
img.save("webcam_image.png")