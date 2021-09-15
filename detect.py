import picar_4wd as fc

speed = 50 # motor power for moves forward and backward
turn = 80 # motor power for turns

def main():
    while True:
        scan_list = fc.scan_step(20) # scan 20cm for every 18 degrees, for 180 degrees total
        if not scan_list:
            continue

        tmp = scan_list[3:7] # only care for the middle 90 degrees, 45 degrees each side
        print(tmp)
        if tmp != [2,2,2,2]: # if object is detected 20cm ... 
            fc.stop() # stop
             fc.time.sleep(0.3)
            fc.backward(speed) # move backwards
            fc.time.sleep(0.3)
            fc.turn_right(turn) # turn to the right
            fc.time.sleep(0.3)
        else:
            fc.forward(speed) # if not, move forward
            fc.time.sleep(0.5)

if __name__ == "__main__":
 try: 
  main()
 finally: 
  fc.stop()