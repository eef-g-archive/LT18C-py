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


def mission06():
    my_drone = Tello()
    mission_params = [30, 180, "", ""]
    drone = HeadsUpTello(my_drone, logging.WARNING, floor=mission_params[0], ceiling=mission_params[1])
    drone.takeoff()

    userInput = 'h'; 

    #go_xyz_speed
    x = 0; 
    y = 0; 

    distance_to_travel = 20; 

    go_straight = False; 

    while userInput != 'q':
        print("~" * 15)
        try:
            if 'f' in userInput:
                drone.drone.move_forward(distance_to_travel); 
                x += distance_to_travel; 
            elif 'b' in userInput:
                drone.drone.move_back(distance_to_travel); 
                x -= distance_to_travel; 
            elif 'r' in userInput:
                drone.drone.move_right(distance_to_travel); 
                y += distance_to_travel; 
            elif 'l' in userInput:
                drone.drone.move_left(distance_to_travel); 
                y -= distance_to_travel; 
            
            elif 'home' in userInput: 
                if go_straight:
                    drone.drone.go_xyz_speed(-x, y, 0, 10); 
                else:
                    drone.drone.go_xyz_speed(-x, 0, 0, 100); 
                    drone.drone.go_xyz_speed(0, y, 0, 100);   
                x = 0; 
                y = 0; 
        
            userInput = input(); 

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