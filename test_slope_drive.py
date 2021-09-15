import picar_4wd as fc
import numpy as np
import picamera
import matplotlib.pyplot as plt

from PIL import Image
from tflite_runtime.interpreter import Interpreter
from picar_4wd.servo import Servo
from picar_4wd.pwm import PWM
import sys

import cv2 

def test():
 total_left = 0
 total_right = 0
 total_forward = 0
 distance = 20
 while total_forward < distance:
     
     ser = Servo(PWM("P0")) # reset angle
     ser.set_angle(0)

     angle_step = 6 # angle step 
     grid = np.zeros((100,100)) # initialize numpy array (origin is 50,0)
     
     prev_x = 0
     prev_y = 0
     
     for i in range (-10,11): #calculate all points of objects
      tmp = fc.get_distance_at(i*angle_step)
      x = 49 + np.int(tmp * np.sin(np.radians(i*angle_step)))
      y = np.int(tmp * np.cos(np.radians(i*angle_step)))
      if x > 99:
       x = 99
      if y > 99:
       y = 99
      grid[x,y] = 1
      
      if (prev_x and prev_y) and (y - prev_y) != 0:
          diff = abs(y - prev_y)
          #print(diff)
          slope = (x-prev_x) / (y-prev_y)
          if slope < 0.5:
              if (y > prev_y):
                   for j in range (0,diff):
                       new_y = y+j
                       new_x = np.int(x+slope*j)
                       if new_x > 99:
                           new_x = 99
                       if new_y > 99:
                           new_y = 99
                       grid[new_x,new_y] = 1
              else:
                   for j in range (0,diff):
                       new_y = prev_y+j
                       new_x = np.int(x+slope*j)
                       if new_x > 99:
                           new_x = 99
                       if new_y > 99:
                           new_y = 99
                       grid[new_x,new_y] = 1
      
     speed4 = fc.Speed(25)
     speed4.start()
     if np.all(grid[40:60,0:10]==0):
      #print(grid[40:60,0:10])
      fc.forward(100)
      x = 0
      fc.time.sleep(0.25)
      speed = speed4()
      x += speed * 0.1
      print(x)
      speed4.deinit()
      total_forward = x + total_forward
      fc.stop()
     else:
      fc.backward(50)
      fc.time.sleep(0.25)
      fc.stop()
      if np.all(grid[55:80,0:10]==0): # detect if something to the left for the car
          print('left')
          fc.turn_left(100) # turn to the left
          fc.time.sleep(3)
          fc.stop()
      else:
          print('right')
          fc.turn_right(100)
          fc.time.sleep(1)
          fc.stop()
          
     print(total_forward)
      
     prev_x = x
     prev_y = y
       
     
     plt.imshow(grid, origin='lower')
     plt.show()

 

if __name__ == "__main__":
 test()
 