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
from Modules.Core.LT18C import DroneController
from Modules.Core.LT18C_Dummy import DummyController
from Modules.Core.Vectors import Vector3
from Modules.Core.motor_control import MotorController, pathing

#-------------------------------------------------------------------------------
# Mission Programs
#-------------------------------------------------------------------------------




def mission07():
    my_drone = Tello()
    mission_params = [60, 180, "PT Student", "Mission 7"]

    # --- Drone setup ---
    # Starting w/ this mission we're going to be using the libraries we made
    # These split the old HeadsUpTello into 2 main parts:
    # The Drone Controller for logic & the Motor Controller for movement
    drone = DroneController(my_drone, logging.WARNING,
     floor=mission_params[0], ceiling=mission_params[1],
     drone_name=mission_params[2], mission_name=mission_params[3])
    motor = MotorController(drone)

    motor.takeoff()

    userInput = 'h'
    while userInput != 'q':
        print("~" * 15)
        if 'f' in userInput:
            motor.forward_cm(int(userInput[2:]))
        elif 'b' in userInput:
            motor.backward_cm(int(userInput[2:]))
        elif 'r' in userInput:
            if 'rot' in userInput:
                motor.rotate_relative_angle(int(userInput[4:]))
            else:
                motor.right_cm(int(userInput[2:]))
        elif 'l' in userInput:
            motor.left_cm(int(userInput[2:]))
        elif 'home' in userInput:
            if 's' in userInput:
                motor.move_absolute(Vector3(0, 0, 0), pathing.direct)
            else:
                motor.move_absolute(Vector3(0, 0, 0), pathing.indirect)
        else:
            print(motor.transform.position)

        userInput = input()

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
        mission07()
        print(f"Mission completed")
    except Exception as excp:
        print(excp)
        print(f"Mission aborted")


if __name__ == '__main__':
    run_mission()