#!/usr/bin/env python3
# Team 3: LT18C

#################
#     MISSION   #
#      LOGS     #
#################
# Flipgrid video: https://flip.com/groups/14186500/topics/34493874/responses/409004974
# Takeoff Measurement: ~35in.
# Celing Measurement (Parameter given was 180cm): ~70in.
# Floor Measurement (Parameter given was 100cm): ~43in.

# Standard python modules
import time
import logging

# Custom modules for the drones
from djitellopy import Tello
from headsupflight import HeadsUpTello

#-------------------------------------------------------------------------------
# Mission Programs
#-------------------------------------------------------------------------------

def mission03():
    my_drone = Tello()
    drone = HeadsUpTello(my_drone, logging.WARNING, floor=100, ceiling=180)
    print(drone.drone.get_height())
    drone.takeoff()
    time.sleep(1)
    drone.fly_to_mission_ceiling()
    time.sleep(2)
    drone.fly_to_mission_floor()
    time.sleep(2)
    drone.land()
    drone.disconnect()
    return
    

#-------------------------------------------------------------------------------
# Python Entry Point
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    try:
        mission03()
        print(f"Mission completed")
    except Exception as excp:
        print(excp)
        print(f"Mission aborted")
