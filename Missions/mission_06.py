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
from Core.LT18C import DroneController
from Core.LT18C_Dummy import DummyController
from Core.Vectors import Vector3;
from Core.motor_control import MotorController, pathing;

import Core.movement_record as Recorder;

#-------------------------------------------------------------------------------
# Mission Programs
#-------------------------------------------------------------------------------

#import turtle; 
#global t; 
#t = turtle.Turtle(); 
#t.left(90); 

#def after_move_turtle(controller, change):
#    t.goto(controller.transform.position.x, controller.transform.position.z); 

#def after_rotation_turtle(controller, change):
#    t.right(change.y); 
    


def mission06():
    my_drone = Tello(); 
    mission_params = [30, 180, "PT-Student", "Mission_06"]; 
    drone = DroneController(my_drone, logging.WARNING, floor=mission_params[0], ceiling=mission_params[1], drone_name=mission_params[2], mission_name=mission_params[3])
    motor = MotorController(drone); 
    Recorder.instantiate(drone); 


    #motor.add_movement_callback(after_move_turtle); 
    #motor.add_rotation_callback(after_rotation_turtle); 
    
    motor.add_movement_invoke(Recorder.record_movement); 
    motor.add_rotation_invoke(Recorder.record_rotation); 


    motor.takeoff()

    userInput = 'h'; 
    distance_to_travel = 40; 

    go_straight = False; 

    while True:
        
        print("~" * 15) 
        userInput = input()

        

        if any(stop_command in userInput for stop_command in ['exit', 'stop', 'quit']):
            print("Landing drone. . .")
            motor.land()
            break; 

        elif 'triangle' in userInput:
            motor.move_absolute(Vector3(0, 0, 0), pathing.triangle); 
        elif 'square' in userInput:
            motor.move_absolute(Vector3(0, 0, 0), pathing.square); 

        elif 'home' in userInput:  
            motor.return_home(go_straight, pathing.square_locked);  
        
        elif 'back track coordinates' in userInput:
            li = [item for item in Recorder.Record.get_coordinate_records()]; 
            while len(li) > 0:
                curr_coord = li.pop(); 
                motor.move_absolute(curr_coord, pathing.direct);  

        elif 'back track' in userInput:
            li = [(item[0], -item[1]) for item in Recorder.Record.get_list()]; 
            #print(li.count, " and ", li); 
            while len(li) > 0:
                command, value = li.pop();   
                if command == Recorder.Type.Move:
                    motor.move_relative(value); 
                else:
                    motor.rotate_relative(value);  
        elif 'f' in userInput:
            motor.forward_cm(distance_to_travel)
        elif 'b' in userInput:
            motor.backward_cm(distance_to_travel)
        elif 'r' in userInput:
            motor.right_cm(distance_to_travel)
        elif 'l' in userInput:
            motor.left_cm(distance_to_travel)
        elif 'j' in userInput:
            motor.move_absolute(Vector3(0, 0, 0), pathing.indirect); 
        elif 'e' in userInput:
            motor.rotate_relative_angle(30); 
        elif 'q' in userInput:
            motor.rotate_relative_angle(-30); 
        elif 'p' in userInput:
            Recorder.print_record(); 
        else: 
            print(motor.transform.forward); 
            print(motor.transform.right); 
            print(motor.transform.up); 

    drone.disconnect()


#-------------------------------------------------------------------------------
# Python Entry Point
#-------------------------------------------------------------------------------
def run_mission(): 

    mission06(); 

    '''
    try:
        mission06(); 
        print(f"Mission completed"); 
    
    except Exception as excp:
        print(excp); 
        print(f"Mission aborted");  
    '''

if __name__ == '__main__':
    run_mission()
