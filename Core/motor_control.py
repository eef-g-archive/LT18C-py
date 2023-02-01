from enum import Enum
import math;
from Core.Vectors import Vector3
from Core.LT18C import DroneController 


class pathing(Enum):
    direct = 0
    indirect = 1
    
    lock = 2

    triangle = 3
    square = 4
    square_locked = 5; 




class MotorController():
 

    def battery_check(self, controller, change: Vector3):
        if (self.controller.get_battery() < self.controller.MIN_OPERATING_POWER):
            self.log.warning(f"*** EMERGENCY LANDING -- BATTERY TOO LOW TO MOVE***")
            self.land()
            raise Exception(f"Minimum Movement Battery Level Error")

    def log_movement(self, controller, change: Vector3):
        self.log.debug(f"Movement function called | new Position: {str(change)}"); 
        self.log.info(f"Drone position prior to moving: {str(self.controller.transform.position)}"); 
    
    def log_post_movement(self, controller, change: Vector3): 
        self.log.info(f"Drone moved successfully. Current Position: {str(self.controller.transform.position)}"); 

    def log_rotation(self, controller, change: Vector3): 
        self.log.debug(f"Rotational function called | new Rotation: {str(change)}"); 
        self.log.info(f"Drone rotation prior to moving: {str(self.controller.transform.rotation)}"); 
    
    def log_post_rotation(self, controller, change: Vector3):
        self.log.info(f"Drone rotated successfully. Current Rotation: {str(self.controller.transform.rotation)}"); 

    def __init__(self, controller: DroneController):
        self.controller:DroneController = controller;    

        self.movement_invoke = [self.log_movement, self.battery_check]; 
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

    def add_rotation_invoke(self, invoke_func):
        self.rotation_callback.append(invoke_func); 
    
    def add_rotation_callback(self, callback_func):
        self.rotation_callback.append(callback_func); 
        

    ########################################################################
    ###################     MOVEMENT FUNCTIONS    ##########################
    ########################################################################
 
    def rotate_relative(self, rotation: Vector3): 
        
        print('rotating from', self.transform.rotation); 

        for invoke in self.rotation_invoke:
            invoke(self.controller, rotation); 
    
        if(rotation.y > 0): 
            self.drone.rotate_clockwise(abs(int(round(rotation.y)))); 
        elif(rotation.y < 0):
            self.drone.rotate_counter_clockwise(abs(int(round(rotation.y)))); 
        else:
            pass; 

        self.controller.transform.rotation.y += rotation.y;          

        for callback in self.rotation_callback:
            callback(self.controller, rotation); 
    
        print('rotating from', self.transform.rotation); 

    def rotate_relative_angle(self, degree: float):
        self.rotate_relative(Vector3(0, degree, 0));  

    def rotate_absolute(self, rotation: Vector3): 
        self.rotate_relative(rotation - self.transform.rotation); 

    def rotate_absolute_angle(self, angle: float): 
        self.rotate_absolute(Vector3(0, angle, 0)); 
     
#######################################################################

    def move_absolute(self, position: Vector3, path:pathing = pathing.direct):
        
        absolute_rotation = self.transform.look_at(position); 
        relative_rotation = (absolute_rotation - self.transform.rotation); 
        distance = self.transform.position.distance(position);  

        match path: 

            case pathing.direct:  

                self.rotate_absolute(self.transform.look_at(position)); 
                self.forward_cm(distance);   
                return; 

            case pathing.triangle: 
                first_turn_angle = 180 / 3;    
                second_turn_angle = -first_turn_angle * 2;     
 

                if(relative_rotation.y < 0):
                    first_turn_angle *= -1; 
                    second_turn_angle *= -1; 
                
                relative_rotation.y += first_turn_angle;  
                
                self.rotate_relative(relative_rotation); 
                self.forward_cm(distance); 
                self.rotate_relative_angle(second_turn_angle); 
                self.forward_cm(distance);  
                return;  

            case pathing.square:  

                if path == pathing.square:
                    first_turn_angle = 180 / 4; 
                 
                second_turn_angle = -first_turn_angle * 2;     

                if path == pathing.square:
                    distance = ((distance ** 2) / 2) ** .5; 

                if(relative_rotation.y < 0):
                    first_turn_angle *= -1; 
                    second_turn_angle *= -1; 
                
                relative_rotation.y += first_turn_angle;  

                self.rotate_relative(relative_rotation); 
                self.forward_cm(distance); 
                self.rotate_relative_angle(second_turn_angle); 
                self.forward_cm(distance);  
                return; 

            case pathing.square_locked:
                
                def get_closest_to_right_angle(angle, base = 90):
                    return base * round(angle/base)

                self.rotate_absolute(self.transform.look_at(position)); 
                angle = self.transform.rotation.y; 


                adjust_angle = get_closest_to_right_angle(angle);  
                
                print("LOCKED ANGLE: ", adjust_angle);   
                self.rotate_absolute(Vector3(0, adjust_angle, 0));  

                print("new rotation(1): ", self.transform.rotation);  

                difference = position - self.transform.position; 


                #FIX
                first_distance = abs(difference.z) 

                if(abs(adjust_angle) == 90 or abs(adjust_angle) == 270):
                    first_distance = abs(difference.x)

                self.forward_cm(first_distance);  
                #END FIX

                second_rotation = self.transform.look_at(position) - self.transform.rotation; 
                self.rotate_relative(second_rotation); 

                print("new rotation(2): ", self.transform.rotation);  

                second_distance = self.transform.position.distance(position); 
                self.forward_cm(second_distance); 

                return; 
            case pathing.indirect: 
                
                dir = (self.transform.position - position).normalized; 

                first_distance = distance * math.cos(math.radians(relative_rotation.y)); 

                #self.move_relative(dir * first_distance); 
                go_back = (-self.transform.forward * first_distance + self.transform.position).distance(position); 
                go_forw = (self.transform.forward * first_distance + self.transform.position).distance(position); 
                if(go_back < go_forw):
                    self.backward_cm(first_distance); 
                else:
                    self.forward_cm(first_distance); 

                second_distance = self.transform.position.distance(position); 

                go_r = (-self.transform.right * second_distance + self.transform.position).distance(position); 
                go_l = (self.transform.right * second_distance + self.transform.position).distance(position); 
                
                if(go_r < go_l): 
                    self.left_cm(second_distance); 
                else:
                    self.right_cm(second_distance); 
                

                return; 
            case _:
                raise Exception("Given pathing does not exist!"); 



    def move_relative(self, position: Vector3, speed = 50):

        print('moving from', self.transform.position); 
        print('current rotation', self.transform.rotation); 

        for invoke in self.movement_invoke:
            invoke(self.controller, position);  

        x = int(round(position.z)); 
        y = int(round(position.x)); 
        z = int(round(position.y)); 

        print("move command: ", x, y, z); 

        #if((abs(x) < 20 and x != 0) or (abs(y) < 20 and y != 0) or (abs(z) < 20 and z != 0)):
        #    print("value less than 20 found, skipping"); 
        #    return; 


        if x > 0:
            self.drone.move_forward(x); 
        elif x < 0:
            self.drone.move_back(abs(x)); 

        if y > 0:
            self.drone.move_right(y); 
        elif y < 0:
            self.drone.move_left(abs(y)); 

        
        self.transform.position += self.transform.forward * position.z;     
        self.transform.position += self.transform.right * position.x;       
        self.transform.position += self.transform.up * position.y;     
        
        print('moved to', self.transform.position); 

        for callback in self.movement_callback:
            callback(self.controller, position); 

    def move_relative_cm(self, x, y, z = 0):  
        self.move_relative(Vector3(x, y, z)); 

    def forward_cm(self, cm):
        self.move_relative_cm(0, 0, cm); 
    
    def backward_cm(self, cm): 
        self.move_relative_cm(0, 0, -cm); 

    def right_cm(self, cm): 
        self.move_relative_cm(cm, 0, 0); 

    def left_cm(self, cm): 
        self.move_relative_cm(-cm, 0, 0);  


    def return_home(self, direct=False, path=pathing.direct):

        self.log.debug(f"return_home function called. | direct = {direct}"); 

        if (self.controller.get_battery() > self.controller.MIN_OPERATING_POWER):
            self.log.info(f"Drone position prior to returning home : [{self.transform.position}]")
            
            self.move_absolute(Vector3(0, 0, 0), path);  

            if self.transform.rotation.y != 0: 
                self.rotate_absolute(Vector3(0, 0, 0));   

            print("Returned Home. Position: ", self.transform.position); 

            self.log.info(f"Drone returned home successfully. Current position: [{self.transform.position}]"); 
        
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

