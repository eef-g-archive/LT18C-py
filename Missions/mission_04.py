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
from Modules.Core.LT18C import DroneController
from Modules.Core.motor_control import MotorController

#-------------------------------------------------------------------------------
# Mission Programs
#-------------------------------------------------------------------------------


def mission04():
    my_drone = Tello()
    mission_params = [30, 180]
    drone = DroneController(my_drone, logging.WARNING, floor=mission_params[0], ceiling=mission_params[1])
    motor = MotorController(drone)
    motor.takeoff()

    userInput = 'h'
    while userInput != 'q':
        print("~" * 15)
        print(f"Current drone height: {drone.drone.get_barometer() - drone.start_barometer}")
        userInput = input("| Enter the number to go up or  down (negative for down): ")
        print("~" * 15)
        try:
            userInput = int(userInput)
            if(userInput > 0):
                motor.up_cm(userInput)
            elif(userInput < 0):
                userInput *= -1
                motor.down_cm(userInput)
        except:
            if userInput == 'q':
                print("Landing drone. . .")
                motor.land()
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