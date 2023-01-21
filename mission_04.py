#!/usr/bin/env python3
# Team 3: LT18C

#################
#     MISSION   #
#      LOGS     #
#################



# Standard python modules
import time
import logging

# Custom modules for the drones
from djitellopy import Tello
from headsupflight import HeadsUpTello

#-------------------------------------------------------------------------------
# Mission Programs
#-------------------------------------------------------------------------------


def mission04():
    my_drone = Tello()
    mission_params = [30, 180]
    drone = HeadsUpTello(my_drone, logging.WARNING, floor=mission_params[0], ceiling=mission_params[1])
    drone.takeoff()

    userInput = 'h'
    while userInput != 'q':
        print("~" * 15)
        print(f"Current drone height: {drone.drone.get_barometer() - drone.start_barometer}")
        userInput = input("| Enter the number to go up or  down (negative for down): ")
        print("~" * 15)
        try:
            userInput = int(userInput)
            if(userInput > 0):
                drone.up(userInput)
            else:
                userInput *= -1
                drone.down(userInput)
        except:
            if userInput == 'q':
                print("Landing drone. . .")
                drone.land()
                break
    drone.disconnect()





def test_up(cm, currHeight, ceiling, floor):
    print(f"Starting height: {currHeight}")
    print(f"Beginning to move up")
    # For the actual up(cm) function, the currHeight will not exist but will be a variable in the drone object
    # --- Same goes for ceiling ---

    # First, see if we can adjust the cm value to fit within the ceiling
    if(currHeight + cm > ceiling):
        cm = ceiling - currHeight

    # If cm is now 0, then just return
    if(cm == 0):
        print("Drone cannot go any higher!")
        return currHeight
    
    
    
    if(cm < 20 and currHeight - 20 >= floor and (currHeight + 20) > ceiling):
        currHeight -= 20
        print(f"Height after lowering temporarily: {currHeight}")
        currHeight += (cm + 20)
        print(f"Height after final adjustment: {currHeight}")

    elif(cm >= 20 and currHeight + cm <= ceiling):
        currHeight += cm
        print(f"Height after final safe ascent: {currHeight}")

    elif(cm < 20 and currHeight - 20 <= ceiling):
        currHeight += 20
        print(f"Current height after raising temporarily: {currHeight}")
        currHeight -= ( 20 - cm)
        print(f"Current height after final adjustment: {currHeight}")
    
    else:
        print(f"ERROR: No possible way to make that move")

    return currHeight


    
def test_down(cm, currHeight, ceiling, floor):
    print(f"=-" * 15)
    print(f"Starting height: {currHeight}")
    print(f"Beginning to move down")
    # For the actual up(cm) function, the currHeight will not exist but will be a variable in the drone object
    # --- Same goes for ceiling ---

    # First, see if we can adjust the cm value to fit within the ceiling
    if(currHeight - cm < floor):
        cm = currHeight - floor
        print(f"New target height: {cm}")
    

    if (cm == 0):
        print(f"Drone already at the floor!")
        return currHeight

    # Need this line bc the default functions will not do anything less than 20 for whatever reason
    if(cm < 20 and currHeight - 20 <= ceiling and (currHeight + 20) > floor):
        currHeight += 20
        print(f"Height after raising temporarily: {currHeight}")
        currHeight -= (cm + 20)
        print(f"Height after final adjustment: {currHeight}")

    elif (cm >= 20 and currHeight - cm > floor):
        currHeight -= cm
        print(f"Current height after final safe descent: {currHeight}")
    
    
 
    
    return currHeight

        
def debug04():
    currHeight = 100
    mission_params = [180, 80]
    userInput = 'h'
    while userInput != 'q':
        print("~"*15)
        print(f"Current drone height: {currHeight}")
        userInput = input("| Enter the number to go up or down (negative for down): ")
        print("~"*15)
        try:
            userInput = int(userInput)
            if(userInput > 0):
                currHeight = test_up(userInput, currHeight, mission_params[0], mission_params[1])
            else:
                userInput *= -1
                print(f"Converted input: {userInput}")
                currHeight = test_down(userInput, currHeight, mission_params[0], mission_params[1])
        except:
            if userInput == 'q':
                print(f"Ending test program. . .")
                break


def bar_testing():
        #mission04()
        drone = Tello()
        drone = HeadsUpTello(drone, logging.WARNING, 30, 60)
        currHeight = 0
        startingPoint = drone.drone.get_barometer()
        while True:
            currPoint = drone.drone.get_barometer()
            print("==============")
            print(f"{currPoint - startingPoint}")
            time.sleep(5)

#-------------------------------------------------------------------------------
# Python Entry Point
#-------------------------------------------------------------------------------
def run_mission():
    try:
        mission04()
        #bar_testing()
        print(f"Mission completed")
    except Exception as excp:
        print(excp)
        print(f"Mission aborted")


if __name__ == '__main__':
    run_mission()
    #debug04()