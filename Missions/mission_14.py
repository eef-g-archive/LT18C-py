#!/usr/bin/env python3
# Team 3: LT18C

#################
#     MISSION   #
#      LOGS     #
#################
# Mission Recording:
# Findings: 


# Standard python modules
import time
import logging

# Custom modules for the drones
from djitellopy import Tello
from Modules.Addons.MicroAdjust import Adjuster 
from Modules.Core.LT18C import DroneController
from Modules.Core.LT18C_Dummy import DummyController
from Modules.Core.Vectors import Vector3;
from Modules.Core.motor_control import MotorController, pathing;

import Modules.Core.movement_record as Recorder;

#-------------------------------------------------------------------------------
# Mission Programs
#-------------------------------------------------------------------------------


def recording_mission():
    print("Beginning mission!")
    my_drone = Tello(); 
    mission_params = [30, 200, "PT-Student", "Mission_14"]; 
    drone = DroneController(my_drone, logging.WARNING, floor=mission_params[0], ceiling=mission_params[1], drone_name=mission_params[2], mission_name=mission_params[3])
    motor = MotorController(drone); 
    Recorder.instantiate(drone); 

    drone.begin_recording(show_feed=True, detect_humans=True)
    while True:
        userInput = input()
        if(userInput == 'q'):
            break
    # motor.takeoff()
    # time.sleep(1)
    # motor.up_cm(60)
    # motor.forward_cm(30)
    # time.sleep(15)
    # motor.backward_cm(30)
    
    # motor.land()
    drone.end_recording()
    drone.disconnect()


#-------------------------------------------------------------------------------
# Python Entry Point
#-------------------------------------------------------------------------------
def run_mission(): 
    try:
        recording_mission(); 
        print(f"Mission completed"); 
    
    except Exception as excp:
        print(excp); 
        print(f"Mission aborted");  

if __name__ == '__main__':
    run_mission()
