from enum import Enum;
from Core.Vectors import Vector3
from Core.LT18C import DroneController 


class pathing(Enum):
    direct = 0
    curved = 1
    triangle = 3
    square = 4


class MotorController():
 
    def log_movement(self, drone, change: Vector3):
        self.log.debug(f"Movement function called | new Position: {str(change)}"); 
        self.log.info(f"Drone position prior to moving: {str(self.controller.transform.position)}"); 
    
    def log_post_movement(self, drone, change: Vector3): 
        self.log.info(f"Drone moved successfully. Current Position: {str(self.controller.transform.position)}"); 

    def log_rotation(self, drone, change: Vector3): 
        self.log.debug(f"Rotational function called | new Rotation: {str(change)}"); 
        self.log.info(f"Drone rotation prior to moving: {str(self.controller.transform.rotation)}"); 
    
    def log_post_rotation(self, drone, change: Vector3):
        self.log.info(f"Drone rotated successfully. Current Rotation: {str(self.controller.transform.rotation)}"); 

    def __init__(self, controller: DroneController):
        self.controller:DroneController = controller;    

        self.movement_invoke = [self.log_movement]; 
        self.movement_callback = [self.log_post_movement]; 
    
        self.rotation_invoke = [self.log_rotation]; 
        self.rotation_callback = [self.log_post_rotation];  

    @property
    def log(self):
        return self.controller.log; 
    @property
    def transform(self):
        return self.controller.transform; 

    @property
    def drone(self):
        return self.controller.drone; 

    @property
    def x(self):
        return self.controller.transform.position.x;  
    @property
    def y(self):
        return self.controller.transform.position.y; 
    @property
    def z(self):
        return self.controller.transform.position.z; 

    @x.setter
    def x(self, new_value:float):
        self.controller.transform.position.x = new_value; 
    @y.setter
    def y(self, new_value:float):
        self.controller.transform.position.y = new_value; 
    @z.setter
    def z(self, new_value:float):
        self.controller.transform.position.z = new_value; 
    

    ########################################################################
    ################### INVOKE/CALLBACK FUNCTIONS ##########################
    ########################################################################

    def add_movement_invoke(self, invoke_func):
        self.movement_invoke.append(invoke_func); 
    
    def add_movement_callback(self, callback_func):
        self.movement_callback.append(callback_func); 

    ########################################################################
    ###################     MOVEMENT FUNCTIONS    ##########################
    ########################################################################
 
    def rotate_relative(self, rotation: Vector3): 
        
        print('rotating from', self.transform.rotation); 

        for invoke in self.rotation_invoke:
            invoke(self.drone, rotation); 
    
        if(rotation.y > 0):
            self.drone.rotate_clockwise(int(rotation.y)); 
        elif(rotation.y < 0):
            self.drone.rotate_counter_clockwise(int(rotation.y)); 

        self.controller.transform.rotation.y += rotation.y;          

        for callback in self.rotation_callback:
            callback(self.drone, rotation); 
    
        print('rotating from', self.transform.rotation); 
    
    def rotation_relative_angular(self, degree: float):
        self.rotate_relative(Vector3(0, degree, 0));  

        

    def move_absolute(self, position: Vector3, path:pathing = pathing.direct): 
        match path:
            case pathing.direct: 
                distance = self.transform.position.distance(position); 
                self.rotate_relative(self.transform.look_at(position)); 
                self.forward_cm(distance);   
                return; 
            case pathing.triangle:
                return; 
            case pathing.square:
                return; 
            case _:
                raise Exception("Given pathing does not exist!"); 



    def move_relative(self, position: Vector3):

        print('moving from', self.transform.position); 
        print('current rotation', self.transform.rotation); 

        for invoke in self.movement_invoke:
            invoke(self.drone, position); 
    
        speed = 50; 

        self.drone.go_xyz_speed(int(position.x), int(position.y), int(position.z), speed);  

        self.transform.position += self.transform.forward * position.x;     
        self.transform.position += self.transform.right * position.y;       
        self.transform.position += self.transform.up * position.z;     
        
        print('moved to', self.transform.position); 

        for callback in self.movement_callback:
            callback(self.drone, position); 

    def move_relative_cm(self, x, y, z = 0):  
        self.move_relative(Vector3(x, y, z)); 

    def forward_cm(self, cm):
        self.move_relative_cm(cm, 0); 
    
    def backward_cm(self, cm): 
        self.move_relative_cm(-cm, 0); 

    def right_cm(self, cm): 
        self.move_relative_cm(0, cm); 

    def left_cm(self, cm): 
        self.move_relative_cm(0, -cm);  


    def return_home(self, direct=False):
        self.log.debug(f"return_home function called. | direct = {direct}"); 

        if (self.controller.get_battery() > self.controller.MIN_OPERATING_POWER):
            self.log.info(f"Drone position prior to returning home : [{self.x}, {self.y}]")
            if direct:
                self.drone.go_xyz_speed(-self.x, self.y, 0, 10); 
            else:
                if (self.x < 0):
                    self.forward_cm(-self.x); 
                else:
                    self.backward_cm(self.x); 
                
                if (self.y < 0):
                    self.right_cm(-self.y); 
                else:
                    self.left_cm(self.y); 

            self.x = 0; 
            self.y = 0; 

            self.log.info(f"Drone returned home successfully. Current position: [{self.x}, {self.y}]"); 
        
        else: 
            self.log.warning(f"ERROR! Aborting command, drone battery less than {self.controller.MIN_OPERATING_POWER}%. Making emergency landing"); 
            self.land();  
    
    def up_cm(self, cm):
        self.log.debug(f"up function called -- cm: {cm}"); 
        if (self.controller.get_battery() > self.controller.MIN_OPERATING_POWER):
            currHeight = self.controller.get_barometer() - self.controller.start_barometer; 
            
            # First, see if we can adjust the cm value to fit within the ceiling
            if(currHeight + cm > self.controller.ceiling):
                cm = self.controller.ceiling - currHeight; 
                self.log.debug(f"Given cm + currHeight > {self.controller.ceiling} | cm value updated to {cm} cm"); 

            # If cm is now 0, then just return
            if(cm == 0):
                self.log.debug("Ending up function, drone cannot go any higher"); 
                return; 
        
            elif (cm < 20):
                self.log.debug("Value given to move up less than 20. Returning."); 
                return; 
        
            else:
                self.log.debug(f"Drone moving up {cm}cm to {cm + currHeight}cm"); 
                self.drone.move_up(cm); 
                self.log.info(f"Drone moved up successfully. New height: {self.controller.get_barometer() - self.controller.start_barometer}")
        else:
            self.log.warning(f"ERROR! Aborting command, drone battery less than {self.controller.MIN_OPERATING_POWER}%. Making emergency landing")
            self.land(); 

    def down_cm(self, cm):
        self.log.debug(f"up function called -- cm: {cm}") 
        if (self.controller.get_battery() > self.controller.MIN_OPERATING_POWER):
            currHeight = self.controller.get_barometer() - self.controller.start_barometer
    
            # For the actual up(cm) function, the currHeight will not exist but will be a variable in the drone object
            # --- Same goes for ceiling ---

            # First, see if we can adjust the cm value to fit within the ceiling
            if(currHeight - cm < self.controller.floor):
                cm = currHeight - self.controller.floor
                print(f"New target height: {cm}"); 
            
            if(cm == 0):
                self.log.debug("Ending up function, drone cannot go any higher")
                return; 
        
            elif (cm < 20):
                self.log.debug("Value given to move up less than 20. Returning.")
                return; 
        
            else:
                self.log.debug(f"Drone moving down {cm}cm to {cm + currHeight}cm")
                self.drone.move_down(cm) 
                self.log.info(f"Drone moved down successfully. New height: {self.controller.get_barometer() - self.controller.start_barometer}")
        else:
            self.log.warning(f"ERROR! Aborting command, drone battery less than {self.controller.MIN_OPERATING_POWER}%. Making emergency landing")
            self.land()  

    def takeoff(self):
        if (self.controller.get_battery() > self.controller.MIN_TAKEOFF_POWER):
            self.log.info("*** TAKEOFF ***"); 
            self.drone.takeoff(); 
            self.log.info(f"Drone height at takeoff: {self.drone.get_height()} cm"); 
        else:
            self.log.warning("*** TAKEOFF FAILED ***"); 
            self.log.warning(f"Drone battery less than {self.controller.MIN_OPERATING_POWER}%, aborting takeoff"); 

    def land(self):
        self.log.info("*** LANDING ***")
        self.drone.land()

