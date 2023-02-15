from enum import Enum
import math;
from Modules.Core.Vectors import Vector3
from Modules.Core.LT18C import DroneController 


class pathing(Enum):
    direct = 0
    indirect = 1
    
    lock = 2

    triangle = 3
    square = 4
    square_locked = 5; 



########################################################################
################### INVOKE/CALLBACK FUNCTIONS ##########################
########################################################################
   


def battery_check(controller, change: Vector3):
    if (controller.get_battery() < controller.MIN_OPERATING_POWER):
        controller.log.warning(f"*** EMERGENCY LANDING -- BATTERY TOO LOW TO MOVE***")
        controller.land()
        raise Exception(f"Minimum Movement Battery Level Error") 

def log_movement(controller, change: Vector3):
    controller.log.debug(f"Movement function called | new Position: {str(change)}"); 
    controller.log.info(f"Drone position prior to moving: {str(controller.transform.position)}"); 

def log_post_movement(controller, change: Vector3): 
    controller.log.info(f"Drone moved successfully. Current Position: {str(controller.transform.position)}"); 

def log_rotation(controller, change: Vector3): 
    controller.log.debug(f"Rotational function called | new Rotation: {str(change)}"); 
    controller.log.info(f"Drone rotation prior to moving: {str(controller.transform.rotation)}"); 

def log_post_rotation(controller, change: Vector3):
    controller.log.info(f"Drone rotated successfully. Current Rotation: {str(controller.transform.rotation)}"); 

    

class MotorController(): 

    def __init__(self, controller: DroneController):
        self.controller:DroneController = controller;   
        self.tether_distance = 5000; 

        self.movement_invoke = [log_movement, battery_check]; 
        self.movement_callback = [log_post_movement]; 
    
        self.rotation_invoke = [log_rotation]; 
        self.rotation_callback = [log_post_rotation];  

        self.controller.motor_controller = self;  

    def add_movement_invoke(self, invoke_func):
        self.movement_invoke.append(invoke_func); 

    def add_movement_callback(self, callback_func):
        self.movement_callback.append(callback_func); 

    def add_rotation_invoke(self, invoke_func):
        self.rotation_callback.append(invoke_func); 

    def add_rotation_callback(self, callback_func):
        self.rotation_callback.append(callback_func);  


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
    def position(self):
        return self.transform.position; 
    @property
    def rotation(self):
        return self.transform.rotation; 
        
    @position.setter
    def position(self, new_position: Vector3):
        self.transform.position = new_position; 

    @rotation.setter
    def rotation(self, new_rotation: Vector3):
        self.transform.rotation = new_rotation;     

    ########################################################################
    ###################     MOVEMENT FUNCTIONS    ##########################
    ########################################################################
 
    def rotate_relative(self, rotation: Vector3):  

        for invoke in self.rotation_invoke:
            invoke(self.controller, rotation); 
    
        if(rotation.y > 0): 
            self.drone.rotate_clockwise(abs(int(round(rotation.y)))); 
        elif(rotation.y < 0):
            self.drone.rotate_counter_clockwise(abs(int(round(rotation.y)))); 
        else: pass; 

        self.controller.transform.rotation.y += rotation.y;          

        for callback in self.rotation_callback:
            callback(self.controller, rotation);  

    def rotate_relative_angle(self, degree: float):
        self.rotate_relative(Vector3(0, degree, 0));  

    def rotate_absolute(self, rotation: Vector3): 
        self.rotate_relative(rotation - self.transform.rotation); 

    def rotate_absolute_angle(self, angle: float): 
        self.rotate_absolute(Vector3(0, angle, 0)); 
     
#######################################################################

    def move_absolute(self, position: Vector3, path:pathing = pathing.direct):
        
        #position = self.calculate_tether_distance(position); 

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
                angle = self.rotation.y;  

                adjust_angle = get_closest_to_right_angle(angle);   
                self.rotate_absolute(Vector3(0, adjust_angle, 0));   

                difference = position - self.transform.position; 
                first_distance = abs(difference.z) 

                if(abs(adjust_angle) == 90 or abs(adjust_angle) == 270):
                    first_distance = abs(difference.x); 

                self.forward_cm(first_distance);    
                second_rotation = self.transform.look_at(position) - self.rotation; 
                self.rotate_relative(second_rotation);   
                second_distance = self.position.distance(position); 
                self.forward_cm(second_distance); 

                return; 
            case pathing.indirect:  
                #position = self.calculate_tether_distance(position); 
                first_distance = distance * math.cos(math.radians(relative_rotation.y)); 
                go_back = (-self.transform.forward * first_distance + self.position).distance(position); 
                go_forw = (self.transform.forward * first_distance + self.position).distance(position); 
                
                if(go_back < go_forw): self.backward_cm(first_distance); 
                else: self.forward_cm(first_distance); 

                second_distance = self.transform.position.distance(position); 
                go_r = (-self.transform.right * second_distance + self.position).distance(position); 
                go_l = (self.transform.right * second_distance + self.position).distance(position); 
                
                if(go_r < go_l): self.left_cm(second_distance); 
                else: self.right_cm(second_distance);   
                return; 
            case _:
                raise Exception("Given pathing does not exist!"); 

    def calculate_tether_distance(self, distance, direction, movementThreshold = 21): 
        if direction.x != 0: full_dist_from_origin = (self.transform.right * distance + self.position).magnitude; 
        elif direction.y != 0: full_dist_from_origin = (self.transform.up * distance + self.position).magnitude; 
        elif direction.z != 0: full_dist_from_origin = (self.transform.forward * distance + self.position).magnitude; 
        else: Vector3.Zero();  
        if(full_dist_from_origin > self.tether_distance):    
            if(self.position.magnitude <= movementThreshold):
                distance = self.tether_distance;   
            else:
                #then this guy is going over the tether line;
                rel_dist = self.position.magnitude; #this is the C
                d_angle = (self.transform.look_at(Vector3(0,0,0)) - self.rotation).y; 
                c_angle_rad = (math.sin(math.radians(d_angle)) * rel_dist)/self.tether_distance; 
                v_angle = 180 - math.degrees(c_angle_rad) - d_angle;  
                v_distance = (rel_dist * math.sin(math.radians(v_angle)))/math.sin(c_angle_rad); 
                distance = v_distance;    
        print(distance); 
        return direction * distance; 

    def handle_movement_limitation(self, movement: Vector3): 
        def sign(value):
            return value / abs(value);  
        def in_bounds(value) -> int:
            if(value < 20): return -1; 
            if(value > 500): return 1; 
            return 0;   
        movement_absolute = abs(movement);    
        next_movement = Vector3.Zero(); 
        new_movement = movement; 

        x_bound, y_bound, z_bound = (in_bounds(movement_absolute.x), in_bounds(movement_absolute.y), in_bounds(movement_absolute.z)); 
        print(x_bound, y_bound, z_bound); 


        if x_bound == 1:
            next_movement.x = movement.x - sign(movement.x) * 500; 
            new_movement.x = 500 * sign(movement.x); 
        if y_bound == 1:
            next_movement.y = movement.y - sign(movement.y) * 500; 
            new_movement.y = 500 * sign(movement.y); 
        if z_bound == 1:
            next_movement.z = movement.z - sign(movement.z) * 500; 
            new_movement.z = 500 * sign(movement.z); 
            
        if x_bound == -1: 
            new_movement.x = 0; 
        if y_bound == -1: 
            new_movement.y = 0; 
        if z_bound == -1: 
            new_movement.z = 0; 

        if next_movement.magnitude < 20: #this is threshhold
            next_movement = None; 

        return new_movement, next_movement; 


    def move_relative(self, movement: Vector3, speed = 50):
        previous_position = self.position;  
        movement = self.calculate_tether_distance(movement.magnitude, movement.normalized); 
        movement, next_movement = self.handle_movement_limitation(movement); 

        for invoke in self.movement_invoke:
            invoke(self.controller, movement);   
        
        self.transform.position += self.transform.forward * movement.z;     
        self.transform.position += self.transform.right * movement.x;       
        self.transform.position += self.transform.up * movement.y;    

        drone_x = int(round(movement.z)); 
        drone_y = int(round(movement.x)); 
        drone_z = int(round(movement.y));  

        if drone_x > 0: self.drone.move_forward(drone_x); 
        elif drone_x < 0: self.drone.move_back(abs(drone_x)); 

        if drone_y > 0: self.drone.move_right(drone_y); 
        elif drone_y < 0: self.drone.move_left(abs(drone_y));  
        
        print('Moved from', previous_position, "to", self.position); 

        for callback in self.movement_callback:
            callback(self.controller, movement); 

        if next_movement is not None:
            print("     The scope of the movement was greater than 500cm."); 
            print("     Moving in smaller increment of", movement); 
            self.move_relative(next_movement, speed);  

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


    def return_home(self, path=pathing.direct):
 

        if (self.controller.get_battery() > self.controller.MIN_OPERATING_POWER):
            self.log.info(f"Drone position prior to returning home : [{self.position}]")
            
            self.move_absolute(Vector3.Zero(), path);  

            if self.transform.rotation.y != 0: 
                self.rotate_absolute(Vector3.Zero());   

            print("Returned Home. Position: ", self.transform.position); 
            self.log.info(f"Drone returned home successfully. Current position: [{self.position}]"); 
        
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

