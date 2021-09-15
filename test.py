import picar_4wd as fc
import numpy as np
import picamera
import matplotlib.pyplot as plt

from PIL import Image
from tflite_runtime.interpreter import Interpreter

import cv2 

def test():
 angle_step = 1 # angle step 
 grid = np.zeros((100,100)) # initialize numpy array (origin is 50,0)
 
 for i in range (-60,61): #calculate all points of objects
  tmp = fc.get_distance_at(i*angle_step)
  x = 49 + np.int(tmp * np.sin(np.radians(i*angle_step)))
  y = np.int(tmp * np.cos(np.radians(i*angle_step)))
  if x > 99: # if outside of the range, just change to the max
   x = 99
  if y > 99:
   y = 99
  grid[x,y] = 1 # if object detected then change to 1
   
 plt.imshow(grid, origin='lower')
 plt.show()

 

if __name__ == "__main__":
 test()
 