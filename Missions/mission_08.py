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
from Core.LT18C_Dummy import DummyController
from Core.Vectors import Vector3
from Core.motor_control import MotorController, pathing

#-------------------------------------------------------------------------------
# Mission Programs
#-------------------------------------------------------------------------------

def mission08():
    my_drone = Tello()
    mission_params = [60, 180, "PT Student", "Mission 8", 10, 15]

    drone = DroneController(my_drone, logging.WARNING,
     floor=mission_params[0], ceiling=mission_params[1],
     drone_name=mission_params[2], mission_name=mission_params[3],
     min_takeoff=mission_params[4], min_operating=mission_params[5])
    motor = MotorController(drone)

    motor.takeoff()
    
    while True:
        motor.forward_cm(20)
        motor.right_cm(20)
        motor.backward_cm(20)
        motor.left_cm(20)        



#-------------------------------------------------------------------------------
# Python Entry Point
#-------------------------------------------------------------------------------
def run_mission():
    try:
        mission08()
        print(f"Mission completed")
    except Exception as excp:
        print(excp)
        print(f"Mission aborted")


if __name__ == '__main__':
    run_mission()