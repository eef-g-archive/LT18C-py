#!/usr/bin/env python3
# Team 3: LT18C

#################
#     MISSION   #
#      LOGS     #
#################
# Mission Recording: https://flip.com/groups/14186500/topics/34494740/responses/409983467 
# Findings: 
# - Drone will be slightly off if starting on an elevated platform
# - Distance the drone moves using the move() function built into the Tello class isn't always the exact same measurement.
# - You can use the built in got_to_xyz method to automate the return home function, but we still included a manual one to know how it works

# Standard python modules
import time
import logging

# Custom modules for the drones
from djitellopy import Tello
from headsupflight import HeadsUpTello

#-------------------------------------------------------------------------------
# Mission Programs
#-------------------------------------------------------------------------------


def mission06():
    my_drone = Tello()
    mission_params = [30, 180, "PT-Student", "Mission_06"]
    drone = HeadsUpTello(my_drone, logging.WARNING, floor=mission_params[0], ceiling=mission_params[1], drone_name=mission_params[2], mission_name=mission_params[3])
    drone.takeoff()

    userInput = 'h'; 
    distance_to_travel = 20; 

    go_straight = False; 

    while userInput != 'q':
        print("~" * 15)
        try:
            if 'f' in userInput:
                drone.forward_cm(distance_to_travel)
            elif 'b' in userInput:
                drone.backward_cm(distance_to_travel)
            elif 'r' in userInput:
                drone.right_cm(distance_to_travel)
            elif 'l' in userInput:
                drone.left_cm(distance_to_travel)
            elif 'home' in userInput: 
                if go_straight:
                    drone.return_home(go_straight)
                else:
                    drone.return_home()
            userInput = input()

        except:
            if userInput == 'q':
                print("Landing drone. . .")
                drone.land()
                break
    drone.disconnect()


#-------------------------------------------------------------------------------
# Python Entry Point
#-------------------------------------------------------------------------------
def run_mission():
    try:
        mission06()
        print(f"Mission completed")
    except Exception as excp:
        print(excp)
        print(f"Mission aborted") 

if __name__ == '__main__':
    run_mission()