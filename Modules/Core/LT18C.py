#!/usr/bin/env python3

from Modules.Core.Transform import Transform
import Modules.Core.dji_matrix as djim
import logging, logging.config
import time 
from djitellopy import Tello; 
from datetime import datetime
import cv2
import threading

from Modules.Core.Vectors import Vector3 
from Modules.Addons.yolo import Yolo_Obj


#------------------------- BEGIN HeadsUpTello CLASS ----------------------------

class DroneController():
    """
    An interface from Team "Heads-Up Flight" to control a DJI Tello RoboMaster 
    Drone. Inherits from the djitellopy.Tello class.
    """

    def __init__(self, drone_baseobject:Tello, debug_level=logging.INFO,
                 floor=0, ceiling=0, drone_name="DroneyMcDroneFace",
                mission_name="Maiden Voyage", min_takeoff=15, min_operating=10):
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
        # Initiate a Yolo_Obj in case we want to use image processing
        self.yolo = Yolo_Obj();
        self.connected = False

        self.transform = Transform();  

        self.MIN_TAKEOFF_POWER = min_takeoff; 
        self.MIN_OPERATING_POWER = min_operating; 

        self.motor_controller = None; 

        now = datetime.now().strftime("%Y%m%d.%H"); 

        logfile = f"{self.drone_name}.{now}.log"; 
        logname = self.drone_name; 


        # Video Feed vars -- start as -1 until initiated w/ start_recording method
        self.video_thread = -1
        self.stop_video_event = -1

        
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
            self.drone.connect();
            self.drone.connect(); 
            self.connected = True; 
            self.log.info("Drone connected successfully"); 
            self.start_barometer = self.drone.get_barometer(); 
        
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
        try:
            if self.connected:
                self.disconnect()
        except Exception as excep:
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

    def cv2TextBoxWithBackground(img, text,
        font=cv2.FONT_HERSHEY_PLAIN,
        pos=(0, 0),
        font_scale=1,
        font_thickness=1,
        text_color=(30, 255, 205),
        text_color_bg=(48, 48, 48)):

        x, y = pos
        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        text_pos = (x, y + text_h + font_scale)
        box_pt1 = pos
        box_pt2 = (x + text_w+2, y + text_h+2)
        cv2.rectangle(img, box_pt1, box_pt2, text_color_bg, cv2.FILLED)
        cv2.putText(img, text, text_pos, font, font_scale, text_color, font_thickness)
        return img

    def take_photo(self):
        self.drone.streamon()
        camera = self.drone.get_frame_read()
        print("Taking picture in 3s ......", end="", flush=True)
        time.sleep(1)
        print("2s... ", end="", flush=True)
        print("1s... ")
        time.sleep(1)
        print("*"*10)
        print("* CLICK! *")
        print("*"*10)

        image = camera.frame
        text = datetime.now().strftime("%Y-%m-%d %H:%m.%S")
        self.cv2TextBoxWithBackground(image, text)
        cv2.imwrite(f"{self.drone_name} Photograph", image)
        time.sleep(0.001)

        print("Press the <ESC> key to quit")
        val = 1.0
        while val >= 1:
            val = cv2.getWindowProperty(f"{self.drone_name} Photograph", cv2.WND_PROP_VISIBLE)
            key_code = cv2.waitKey(100)
            if key_code & 0xFF == 27:
                break
        print("Destroying the picture window")
        cv2.destroyAllWindows()
        self.drone.streamoff()

    def process_video_feed(self, stop_thread_event, display_video_live=False, detect_humans=False):

        movie_name = f'{self.drone_name}_{self.mission_name}_capture.avi'
        movie_codec = cv2.VideoWriter_fourcc(*"mp4v")
        movie_fps = 20
        frame_wait = 1 / movie_fps
        movie_size = (360, 240)

        print("Thread started")
        self.drone.streamon()
        camera = self.drone.get_frame_read()
        movie = cv2.VideoWriter(movie_name, movie_codec, movie_fps, movie_size, True)
        time_prev = time.time()
        if display_video_live:
            cv2.namedWindow(f"{self.drone_name} Video Feed")
        print("Video feed started")

        frame_count = 0
        while not stop_thread_event.isSet():

            time_curr = time.time()
            time_elapsed = time_curr - time_prev
            if time_elapsed > frame_wait:
                image = camera.frame
                image = cv2.resize(image, movie_size)
                if(frame_count == movie_fps):
                    image = self.yolo.analyze_frame(image)
                    frame_count = 0
                if display_video_live:
                    cv2.imshow(f"{self.drone_name} Video Feed", image)
                cv2.waitKey(1)
                movie.write(image)
                time_prev = time_curr
                frame_count += 1

            if display_video_live:
                cv2.waitKey(5)
            else:
                time.sleep(0.005)

        print("Stopping video feed")
        self.drone.streamoff()
        movie.release()
        print("Thread finished")

    def begin_recording(self, show_feed = False, detect_humans=False):
        self.stop_video_event = threading.Event()
        self.video_thread = threading.Thread(target=self.process_video_feed, args=(self.stop_video_event, show_feed, detect_humans))
        self.video_thread.setDaemon(True)
        self.video_thread.start()
        
    def end_recording(self):
        self.stop_video_event.set()
        self.video_thread.join(0.5)
        print("Destroying all picture windows")
        cv2.destroyAllWindows()

    
#------------------------- END OF HeadsUpTello CLASS ---------------------------