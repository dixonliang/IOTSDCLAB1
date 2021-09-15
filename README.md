# Self-Driving Toy Car (Internet of Things, CS-437 University of Illinois at Urbana-Champaign)

**Video Demo: https://youtu.be/t4X64sTeJ_0**

[**Lab Report: IoT_Lab1_SDC.pdf**](https://github.com/dixonliang/IOTSDCLAB1/blob/main/IoT_Lab1_SDC.pdf)

### Overview

Note: The baseline code from this repo, https://github.com/sunfounder/picar-4wd will needed for the code files in this repo to function. 

This repo contains the files for Lab 1 of the IoT course, CS-437 as part of the Masters in Computer Science program at UIUC. The objective of Lab 1 was to create and program an autonomous car. The car has the ability of basic obstacle avoidance, mapping/navigation, and image detection. A full lab write up is included in this repo as is a video demo. 

![alt text](https://github.com/dixonliang/IOTSDCLAB1/blob/main/step1_picture.jpeg)

### Directory

detect.py: Contains the code for basic object avoidance. 

detect_picamera: Contains the code for image detection, specifically stopping at a stop sign. 

test: Contains the code for mapping, using a reading per degree of the ultrasonic sensor. 

test_slope: Contains the code for mapping, using a reading per six degrees of the ultrasonic sensor. Slope interpolation is then used to fill in the gaps.

test_slope_drive: Contains the code for basic routing/naviagtion by using the mapping and avoidance code. Distance is also tracked for routing purposes. 

full_Test: Contains the code for the full test of the routing and navigation combined with image detection so that the car will stop when it sees a stop sign. 


