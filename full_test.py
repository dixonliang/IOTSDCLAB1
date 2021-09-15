from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PIL import Image
from tflite_runtime.interpreter import Interpreter
from picar_4wd.servo import Servo
from picar_4wd.pwm import PWM

import picar_4wd as fc
import numpy as np
import picamera
import matplotlib.pyplot as plt
import sys
import cv2
import argparse
import io
import re
import time


CAMERA_WIDTH = 600
CAMERA_HEIGHT = 400
threshold = 0.60
    
def load_labels(path):
  """Loads the labels file. Supports files with or without index numbers."""
  with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    labels = {}
    for row_number, content in enumerate(lines):
      pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
      if len(pair) == 2 and pair[0].strip().isdigit():
        labels[int(pair[0])] = pair[1].strip()
      else:
        labels[row_number] = pair[0].strip()
  return labels


def set_input_tensor(interpreter, image):
  """Sets the input tensor."""
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def get_output_tensor(interpreter, index):
  """Returns the output tensor at the given index."""
  output_details = interpreter.get_output_details()[index]
  tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
  return tensor


def detect_objects(interpreter, image, threshold):
  """Returns a list of detection results, each a dictionary of object info."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()

  # Get all output details
  classes = get_output_tensor(interpreter, 1)
  scores = get_output_tensor(interpreter, 2)
  count = int(get_output_tensor(interpreter, 3))

  results = []
  for i in range(count):
    if scores[i] >= threshold:
      result = {
          'class_id': classes[i],
          'score': scores[i]
      }
      results.append(result)
  return results

def test():
 labels = load_labels('/home/pi/picar-4wd/examples/coco/coco_labels.txt')
 interpreter = Interpreter('/home/pi/picar-4wd/examples/coco/detect.tflite')
 interpreter.allocate_tensors()
 _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']
 
 with picamera.PiCamera(
      resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
    #camera.start_preview()
    try:
      stream = io.BytesIO()
      distance = 25
      total_forward = 0
      while total_forward < distance:
         for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
          stream.seek(0)
          image = Image.open(stream).convert('RGB').resize(
            (input_width, input_height), Image.ANTIALIAS)
          results = detect_objects(interpreter, image, threshold)
        
     
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
           fc.forward(100)
           x = 0
           fc.time.sleep(1)
                        
           speed = speed4()
           x += speed * 0.5
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
              fc.time.sleep(2)
              fc.stop()
              
          print(total_forward)
          
          prev_x = x
          prev_y = y
          
          for obj in results:
            if (labels[obj['class_id']] == 'stop sign'):
             print(labels[obj['class_id']])
             fc.stop()
             fc.time.sleep(4)
          stream.seek(0)
          stream.truncate()

          #plt.imshow(grid, origin='lower')
          #plt.show()
      fc.stop() 
             

    finally:
      camera.stop_preview()


if __name__ == "__main__":
 test()
 