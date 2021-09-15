from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import io
import re
import time

from annotation import Annotator

import picar_4wd as fc
import numpy as np
import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter

CAMERA_WIDTH = 600
CAMERA_HEIGHT = 400
threshold = 0.75
    
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

def main():
  distance = 20
  labels = load_labels('/home/pi/picar-4wd/examples/coco/coco_labels.txt')
  interpreter = Interpreter('/home/pi/picar-4wd/examples/coco/detect.tflite')
  interpreter.allocate_tensors()
  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

  with picamera.PiCamera(
      resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
    #camera.start_preview()
    try:
      stream = io.BytesIO()
      annotator = Annotator(camera)
      total = 0
      while total <= distance:
       speed4 = fc.Speed(25)
       speed4.start()
       fc.forward(10)
       x = 0
       camera.capture(stream, format='jpeg', use_video_port=True)
       stream.seek(0)
       image = Image.open(stream).convert('RGB').resize(
            (input_width, input_height), Image.ANTIALIAS)
       start_time = time.monotonic()
       results = detect_objects(interpreter, image, threshold)
       elapsed_ms = (time.monotonic() - start_time) * 1000

       annotator.clear()
       for obj in results:
         if (labels[obj['class_id']] == 'stop sign'):
            print(labels[obj['class_id']])
            fc.stop()
            fc.time.sleep(3)
            
       fc.time.sleep(0.1)
       speed = speed4()
       x += speed * 0.10
       speed4.deinit()
       total = x + total
       print(total)
       
       annotator.update()

       stream.seek(0)
       stream.truncate()
       
      fc.stop()

    finally:
      camera.stop_preview()


if __name__ == '__main__':
  main()
