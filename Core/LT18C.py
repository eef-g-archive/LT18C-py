#!/usr/bin/env python3

import Core.dji_matrix as djim
import logging, logging.config
import time 
from djitellopy import Tello; 
from datetime import datetime

from Core.objects import Vector3


#------------------------- BEGIN HeadsUpTello CLASS ----------------------------

class DroneController():
    """
    An interface from Team "Heads-Up Flight" to control a DJI Tello RoboMaster 
    Drone. Inherits from the djitellopy.Tello class.
    """

    def __init__(self, drone_baseobject:Tello, debug_level=logging.INFO,
                 floor=0, ceiling=0, drone_name="DroneyMcDroneFace",
                mission_name="Maiden Voyage"):
        """
        Constuctor that establishes a connection with the drone. Pass in a new
        djitellopy Tello object give your HeadsUpTello object its wings.

        Arguments
            drone_baseobject: A new djitellopy.Tello() object
            debug_level:      Set the desired logging level.
                              logging.INFO shows every command and response 
                              logging.WARN will only show problems
                              There are other possibilities, see logging module
        """

        # HeadsUpTello class uses the design principal of composition (has-a)
        # instead of inheritance (is-a) so that we can choose between the real
        # drone and a simulator. If we had used inheritance, we would be forced
        # to choose one or the other.
        self.drone_name = drone_name
        self.mission_name = mission_name
        self.drone:Tello = drone_baseobject
        self.drone.LOGGER.setLevel(debug_level)
        self.floor = floor
        self.ceiling = ceiling

        self.position = Vector3(0,0,0); 
        self.rotation = 0.0; 

        self.x = 0
        self.y = 0

        self.MIN_TAKEOFF_POWER = 15
        self.MIN_OPERATING_POWER = 10


        now = datetime.now().strftime("%Y%m%d.%H")
        logfile = f"{self.drone_name}.{now}.log"
        logname = self.drone_name
        # Thanks to Yogesh Yadav's example with Stream Handler and File Handler:
        #   https://stackoverflow.com/questions/7507825 (not the winning answer)
        # Configure the logger so that DEBUG messages and higher are logged to file but
        #   only WARNINGS and higher are printed to stderr

        log_settings = {
            'version':1,
            'disable_existing_loggers': False,
            'handlers': {
                'error_file_handler': {
                    'level': 'DEBUG',
                    'formatter': 'drone_errfile_fmt',
                    'class': 'logging.FileHandler',
                    'filename': logfile,
                    'mode': 'a',
                },
                'debug_console_handler': {
                    'level': 'WARNING',
                    'formatter': 'drone_stderr_fmt',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stderr',
                },    
            },    
            'formatters': {
                'drone_errfile_fmt': {
                    'format': '%(asctime)s|%(levelname)s: %(message)s [%(name)s@%(filename)s.%(funcName)s.%(lineno)d]',
                    'datefmt': '%Y-%m-%dT%H:%M:%S'
                },
                'drone_stderr_fmt': {
                    'format': '%(levelname)s: %(message)s [%(name)s@%(filename)s.%(funcName)s.%(lineno)d]',
                },
            },
            'loggers': {
                logname: {
                    'handlers' :['debug_console_handler', 'error_file_handler'],
                    'level': 'DEBUG',
                    'propagate': False,
                },
            },
        }
        logging.config.dictConfig(log_settings)

        self.log = logging.getLogger(logname)
        self.log.info("Logger initialized")


        try:
            self.drone.connect()
            self.connected = True
            self.log.info("Drone connected successfully")
            self.start_barometer = self.drone.get_barometer()
        except Exception as excp:
            print(f"ERROR: could not connect to Trello Drone: {excp}")
            print(f" => Did you pass in a valid drone base object?")
            print(f" => Verify that your firewall allows UDP ports 8889 and 8890")
            print(f"    The Chromebook's firewall reverts to default settings every")
            print(f"    time that you restart the virtual Linux environment.")
            print(f" => You may need to connect to the drone with the Trello App.")
            self.log.warning("Could not connect to drone")
            self.disconnect()
            raise
        return


    def __del__(self):
        """ Destructor that gracefully closes the connection to the drone. """
        if self.connected:
            self.disconnect()
        return


    def disconnect(self):
        """ Gracefully close the connection with the drone. """
        self.drone.end()
        self.connected = False
        self.log.info("Drone disconnected")
        print(f"Drone connection closed gracefully")
        return


    def top_led_color(self, red:int, green:int, blue:int):
        """
        Change the top LED to the specified color. The colors don't match the
        normal RGB palette very well.

        Arguments
            red:   0-255
            green: 0-255
            blue:  0-255
        """

        r = djim.capped_color(red)
        g = djim.capped_color(green)
        b = djim.capped_color(blue)
        cmd = f"EXT led {r} {g} {b}"
        self.drone.send_control_command(cmd)
        return
            

    def top_led_off(self):
        """ Turn off the top LED. """

        cmd = f"EXT led 0 0 0"
        self.drone.send_control_command(cmd)
        return


    def matrix_pattern(self, flattened_pattern:str, color:str='b'):
        """
        Show the flattened pattern on the LED matrix. The pattern should be 
        64 letters in a row with values either (r)ed, (b)lue, (p)urple, or (0)
        off. The first 8 characters are the top row, the next 8 are the second
        row, and so on.
        
        Arguments
            flattened_pattern: see examples in dji_matrix.py
            color:             'r', 'b', or 'p'
        """

        if color.lower() not in "rpb":
            color = 'b'
        cmd = f"EXT mled g {flattened_pattern.replace('*', color.lower())}"
        self.drone.send_control_command(cmd)
        return


    def matrix_off(self):
        """ Turn off the 64 LED matrix. """
        
        off_pattern = "0" * 64
        self.matrix_pattern(off_pattern)
        return


    def get_battery(self):
        """ Returns the drone's battery level as a percent. """
        self.log.debug(f"get_battery function called -- Output: {self.drone.get_battery()}")
        return self.drone.get_battery()


    def get_barometer(self):
        """ Returns the drone's current barometer reading in cm. """
        self.log.debug(f"get_barometer function called -- Output: {self.drone.get_barometer()}")
        return self.drone.get_barometer()


    def get_temperature(self):
        """ Returns the drone's internal temperature in °F. """
        self.log.debug(f"get_temperature function called -- Output: {self.drone.get_temperature()}")
        return self.drone.get_temperature() 


    def fly_to_mission_ceiling(self):
        self.log.debug(f"fly_to_mission_ceiling function called -- Going to {self.ceiling} cm")
        if(self.drone.get_battery() > self.MIN_OPERATING_POWER):
            h = self.drone.get_height()
            while(h < self.ceiling):
                if h + 20 < self.ceiling:
                    self.drone.move_up(20)
                    print("Trying to move up by 20 units")
                else:
                    print("I cannot move up anymore!")
                    break
                h = self.drone.get_height()
                print(f"My current height is: '{h}'")
                if h == self.ceiling:
                    break
            print("Ceiling reached | Hovering for 10 seconds to test measurement")
            self.log.info(f"Mission ceiling reached. Drone height: {self.drone.get_height()} cm")
            time.sleep(10)
        else:
            self.log.warning("ERROR: Drone battery less than 10%, aborting command and landing")
            self.land()

    def fly_to_mission_floor(self):
        self.log.debug(f"fly_to_mission_floor function called -- Going to {self.floor} cm")
        if (self.drone.get_battery() > self.MIN_OPERATING_POWER):
            h = self.drone.get_height()
            while (h > self.floor):
                if h + 20 > self.floor:
                    self.drone.move_down(20)
                    print("Trying to move down 20 units")
                else:
                    print("I have reached the floor already, I can't go lower! D:")
                    break
                h = self.drone.get_height()
                print(f"My current height is: '{h}'")
                if h == self.floor:
                    break
            print("Floor reached | Hovering for 10 seconds to test measurement")
            self.log.info(f"Mission floor reached. Drone height: {self.drone.get_height()} cm")
            time.sleep(10)
        else:
            self.log.warning("ERROR: Drone battery less than 10%, aborting command and landing")
            self.land()
        


#------------------------- END OF HeadsUpTello CLASS ---------------------------