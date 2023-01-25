#!/usr/bin/env python3
# Team 3: LT18C

#################
#     MISSION   #
#      LOGS     #
#################

# Video Link: https://flip.com/groups/14186500/topics/34494288/responses/409752384
# Findings:
#   Barometer is slightly more accurate
#   Height would be off, but would be off by larger amounts
#   Barometer, however, is entirely dependent on how you do your math & keeping track from the very beginning


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
            elif(userInput < 0):
                userInput *= -1
                drone.down(userInput)
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
        mission04()
        print(f"Mission completed")
    except Exception as excp:
        print(excp)
        print(f"Mission aborted")


if __name__ == '__main__':
    run_mission()