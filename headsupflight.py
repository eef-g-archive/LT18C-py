#!/usr/bin/env python3

import dji_matrix as djim
import logging
import time


#------------------------- BEGIN HeadsUpTello CLASS ----------------------------

class HeadsUpTello():
    """
    An interface from Team "Heads-Up Flight" to control a DJI Tello RoboMaster 
    Drone. Inherits from the djitellopy.Tello class.
    """

    def __init__(self, drone_baseobject, debug_level=logging.INFO,
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
        self.drone = drone_baseobject
        self.drone.LOGGER.setLevel(debug_level)
        self.floor = floor
        self.ceiling = ceiling

        try:
            #self.drone.connect()
            self.drone.connect()
            self.connected = True
            self.start_barometer = self.drone.get_barometer()
        except Exception as excp:
            print(f"ERROR: could not connect to Trello Drone: {excp}")
            print(f" => Did you pass in a valid drone base object?")
            print(f" => Verify that your firewall allows UDP ports 8889 and 8890")
            print(f"    The Chromebook's firewall reverts to default settings every")
            print(f"    time that you restart the virtual Linux environment.")
            print(f" => You may need to connect to the drone with the Trello App.")
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
        return self.drone.get_battery()


    def get_barometer(self):
        """ Returns the drone's current barometer reading in cm. """
        return self.drone.get_barometer()


    def get_temperature(self):
        """ Returns the drone's internal temperature in °F. """
        return self.drone.get_temperature()



    def takeoff(self):

        self.drone.takeoff()

    def land(self):

        self.drone.land()




    def fly_to_mission_ceiling(self):
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
        time.sleep(10)

    def fly_to_mission_floor(self):
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
        time.sleep(10)

    def up(self, cm):
        print(f"=-"*15)
        currHeight = self.drone.get_barometer() - self.start_barometer
        print(f"Current height: {currHeight}")
        # First, see if we can adjust the cm value to fit within the ceiling
        if(currHeight + cm > self.ceiling):
            cm = self.ceiling - currHeight
            print(f"New cm: {cm}")

        # If cm is now 0, then just return
        if(cm == 0):
            print("Drone cannot go any higher!")
            return
        
        if(cm < 20 and currHeight - 20 >= self.floor and (currHeight + 20) > self.ceiling):
            print(f"Entered if statement #1")
            self.drone.move_down(20)
            print(f"Height after lowering temporarily: {self.drone.get_barometer() - self.start_barometer}")
            self.drone.move_up(cm + 20)

        elif(cm >= 20 and currHeight + cm <= self.ceiling):
            print(f"Entered if statement #2")
            self.drone.move_up(cm)            

        elif(cm < 20 and currHeight - 20 <= self.ceiling):
            print(f"Entered if statement 3")
            self.drone.move_up(20)
            print(f"Current height after raising temporarily: {self.drone.get_barometer() - self.start_barometer}")
            self.drone.move_down(20 + cm)
        
        elif (cm > 20 and currHeight + cm >= self.ceiling):
            print(f"Entered if statement 4")
            self.drone.move_up(self.ceiling - currHeight)

        else:
            print(f"ERROR: No possible way to make that move")


        print(f"Height after final safe ascent: {self.drone.get_barometer() - self.start_barometer}")
    def down(self, cm):
        currHeight = self.drone.get_barometer() - self.start_barometer

        print(f"=-" * 15)
        print(f"Current height: {currHeight}")
        print(f"Beginning to move down")
        # For the actual up(cm) function, the currHeight will not exist but will be a variable in the drone object
        # --- Same goes for ceiling ---

        # First, see if we can adjust the cm value to fit within the ceiling
        if(currHeight - cm < self.floor):
            cm = currHeight - self.floor
            print(f"New target height: {cm}")
        

        if (cm == 0):
            print(f"Drone already at the floor!")
            return 

        # Need this line bc the default functions will not do anything less than 20 for whatever reason
        if(cm < 20 and currHeight - 20 <= self.ceiling and (currHeight + 20) > self.floor):
            self.drone.move_up(20)
            print(f"Height after raising temporarily: {self.drone.get_barometer() - self.start_barometer}")
            self.drone.move_down(cm + 20)
            print(f"Height after final adjustment: {self.drone.get_barometer() - self.start_barometer}")

        elif (cm >= 20 and currHeight - cm > self.floor):
            self.drone.move_down(cm)
            print(f"Current height after final safe descent: {self.drone.get_barometer() - self.start_barometer}")
        
    
        



#------------------------- END OF HeadsUpTello CLASS ---------------------------