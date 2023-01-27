from Core.LT18C import DroneController 

class MotorController():

    def __init__(self, controller: DroneController):
        self.controller = controller;  

        self.rotation:float = 0; 


    @property
    def log(self):
        return self.controller.log; 

    @property
    def x(self):
        return self.controller.position.x;  
    @property
    def y(self):
        return self.controller.position.y; 

    @x.setter
    def x(self, new_value:float):
        self.controller.position.x = new_value; 
    @y.setter
    def y(self, new_value:float):
        self.controller.position.y = new_value; 
    

    
    def forward_cm(self, cm):
        self.log.debug(f"forward_cm function called | cm: {cm}")
        self.log.info(f"Drone position prior to moving: [{self.x}, {self.y}]")
        self.controller.drone.move_forward(cm)
        self.x += cm
        self.log.info(f"Drone moved forward successfully. Current position: [{self.x}, {self.y}]")
    
    def backward_cm(self, cm):
        self.log.debug(f"backward_cm function called | cm: {cm}")
        self.log.info(f"Drone position prior to moving backwards: [{self.x}, {self.y}]")
        self.controller.drone.move_back(cm)
        self.x -= cm
        self.log.info(f"Drone move backwards  successfully. Current position: [{self.x}, {self.y}]")

    def right_cm(self, cm):
        self.log.debug(f"right_cm function called | cm: {cm}")
        self.log.info(f"Drone position prior to moving right: [{self.x}, {self.y}]")
        self.controller.drone.move_right(cm)
        self.y += cm
        self.log.info(f"Drone moved right successfully. Current position: [{self.x}, {self.y}]")

    def left_cm(self, cm):
        self.log.debug(f"left_cm function called. | cm: {cm}")
        self.log.info(f"Drone position prior to moving left: [{self.x}, {self.y}]")
        self.controller.drone.move_left(cm)
        self.y -= cm
        self.log.info(f"Drone moved left successfully. Current position: [{self.x}, {self.y}]")
  
    def return_home(self, direct=False):
        self.log.debug(f"return_home function called. | direct = {direct}");

        if (self.controller.drone.get_battery() > self.controller.MIN_OPERATING_POWER):
            self.log.info(f"Drone position prior to returning home : [{self.x}, {self.y}]")
            if direct:
                self.controller.drone.go_xyz_speed(-self.x, self.y, 0, 10)
            else:
                if (self.x < 0):
                    self.forward_cm(-self.x)
                else:
                    self.backward_cm(self.x)
                
                if (self.y < 0):
                    self.right_cm(-self.y)
                else:
                    self.left_cm(self.y)

            self.x = 0; 
            self.y = 0; 

            self.log.info(f"Drone returned home successfully. Current position: [{self.x}, {self.y}]")
        else: 
            self.log.warning(f"ERROR! Aborting command, drone battery less than {self.controller.MIN_OPERATING_POWER}%. Making emergency landing")
            self.land(); 

    


    def up_cm(self, cm):
        self.log.debug(f"up function called -- cm: {cm}") 
        if (self.controller.drone.get_battery() > self.controller.MIN_OPERATING_POWER):
            currHeight = self.controller.drone.get_barometer() - self.controller.start_barometer
            
            # First, see if we can adjust the cm value to fit within the ceiling
            if(currHeight + cm > self.controller.ceiling):
                cm = self.controller.ceiling - currHeight
                self.log.debug(f"Given cm + currHeight > {self.controller.ceiling} | cm value updated to {cm} cm")

            # If cm is now 0, then just return
            if(cm == 0):
                self.log.debug("Ending up function, drone cannot go any higher")
                return
            elif (cm < 20):
                self.log.debug("Value given to move up less than 20. Returning.")
                return
            else:
                self.log.debug(f"Drone moving up {cm}cm to {cm + currHeight}cm")
                self.controller.drone.move_up(cm) 
                self.log.info(f"Drone moved up successfully. New height: {self.controller.drone.get_barometer() - self.controller.start_barometer}")
        else:
            self.log.warning(f"ERROR! Aborting command, drone battery less than {self.controller.MIN_OPERATING_POWER}%. Making emergency landing")
            self.land()

    
    def down_cm(self, cm):
        self.log.debug(f"up function called -- cm: {cm}") 
        if (self.controller.drone.get_battery() > self.controller.MIN_OPERATING_POWER):
            currHeight = self.controller.drone.get_barometer() - self.controller.start_barometer
    
            # For the actual up(cm) function, the currHeight will not exist but will be a variable in the drone object
            # --- Same goes for ceiling ---

            # First, see if we can adjust the cm value to fit within the ceiling
            if(currHeight - cm < self.controller.floor):
                cm = currHeight - self.controller.floor
                print(f"New target height: {cm}")
            
            if(cm == 0):
                self.log.debug("Ending up function, drone cannot go any higher")
                return
            elif (cm < 20):
                self.log.debug("Value given to move up less than 20. Returning.")
                return
            else:
                self.log.debug(f"Drone moving down {cm}cm to {cm + currHeight}cm")
                self.controller.drone.move_down(cm) 
                self.log.info(f"Drone moved down successfully. New height: {self.controller.drone.get_barometer() - self.controller.start_barometer}")
        else:
            self.log.warning(f"ERROR! Aborting command, drone battery less than {self.controller.MIN_OPERATING_POWER}%. Making emergency landing")
            self.land()  

    def takeoff(self):
        if (self.controller.drone.get_battery() > self.controller.MIN_TAKEOFF_POWER):
            self.log.info("*** TAKEOFF ***")
            self.controller.drone.takeoff()
            self.log.info(f"Drone height at takeoff: {self.controller.drone.get_height()} cm")
        else:
            self.log.warning("*** TAKEOFF FAILED ***")
            self.log.warning("Drone battery less than 15%, aborting takeoff")


    def land(self):
        self.log.info("*** LANDING ***")
        self.controller.drone.land()

