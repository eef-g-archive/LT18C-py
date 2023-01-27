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
from Core.LT18C import DroneController
from Core.motor_control import MotorController
#-------------------------------------------------------------------------------
# Mission Programs
#-------------------------------------------------------------------------------


def mission04():
    my_drone = Tello()
    mission_params = [30, 180, "PT Student", "Mission 5"]
    drone = DroneController(my_drone, logging.WARNING, floor=mission_params[0], ceiling=mission_params[1], drone_name=mission_params[2], mission_name=mission_params[3])
    motor = MotorController(drone)
    motor.takeoff()

    userInput = 'h'
    while userInput != 'q':
        print("~" * 15)
        print(f"Current drone height: {drone.get_barometer() - drone.start_barometer}")
        userInput = input("| Enter the number to go up or  down (negative for down): ")
        print("~" * 15)
        try:
            userInput = int(userInput)
            if(userInput > 0):
                motor.up_cm(userInput)
            elif (userInput < 0):
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