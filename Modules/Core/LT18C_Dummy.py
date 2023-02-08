#!/usr/bin/env python3

from Modules.Core.DummyDrone import DummyDrone
from Modules.Core.Transform import Transform
import Modules.Core.dji_matrix as djim
import logging, logging.config
import time 
from djitellopy import Tello; 
from datetime import datetime

from Modules.Core.Vectors import Vector3


#------------------------- BEGIN HeadsUpTello CLASS ----------------------------

class DummyController():
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
        self.drone_name = drone_name; 
        self.connected = False; 
        
        self.drone = DummyDrone(); 

        self.mission_name = mission_name; 
        self.floor = floor; 
        self.ceiling = ceiling; 

        self.transform = Transform(); 

        self.x = 0; 
        self.y = 0; 

        self.MIN_TAKEOFF_POWER = 15; 
        self.MIN_OPERATING_POWER = 10; 

        now = datetime.now().strftime("%Y%m%d.%H"); 
        logfile = f"{self.drone_name}.{now}.log"; 
        logname = self.drone_name; 
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
            #self.drone.connect()
            self.connected = True
            self.log.info("Drone connected successfully") 
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
        self.connected = False
        self.log.info("Drone disconnected")
        print(f"Drone connection closed gracefully")
        return; 
              

    def get_battery(self) -> int:
        """ Returns the drone's battery level as a percent. """
        self.log.debug(f"get_battery function called -- Output: {self.drone.get_battery()}")
        return 100; 


    def get_barometer(self) -> int:
        """ Returns the drone's current barometer reading in cm. """
        self.log.debug(f"get_barometer function called -- Output: {self.drone.get_barometer()}")
        return 2200; 


    def get_temperature(self) -> int:
        """ Returns the drone's internal temperature in °F. """
        self.log.debug(f"get_temperature function called -- Output: {self.drone.get_temperature()}")
        return 25;  


#------------------------- END OF HeadsUpTello CLASS ---------------------------