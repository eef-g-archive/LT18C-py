from Modules.Core.LT18C import DroneController
from Modules.Core.Vectors import Vector3

class Adjuster(object):

    def __init__(self, controller):
        self.controller:DroneController = controller; 
        self.current_distance:float = 0;  

        self.controller.motor_controller.add_movement_invoke(self.pre_move_check); 
        self.controller.motor_controller.add_movement_callback(self.post_move_check); 


    def get_tof(self): 
        response = self.controller.drone.send_command_with_return("EXT tof?"); 
        print('\n\n\n', response, '\n\n\n');
        cm = int(response.split(' ')[1]) / 10; 
        return cm; 


    def pre_move_check(self, controller:DroneController, position:Vector3):
        if(int(position.z) == 0):
            return; 
        
        self.current_distance = self.get_tof(); 

    def post_move_check(self, controller:DroneController, position:Vector3):
        if(int(position.z) == 0):
            return; 
        
        previous_distance = self.current_distance; 
        curr_distance = self.get_tof(); 
        tof_difference = previous_distance - curr_distance; 

        print("\nPrev Dist: ", previous_distance); 
        print("Post Dist: ", curr_distance); 

        if (tof_difference >= 100):
            print("Somesing went wong. Distan is too wong."); 
            return; 
        
        net_difference = position.z - tof_difference; 

        print("\nPos Z: ", position.z, "\nTOF DIFF: " , tof_difference); 
        print("DIFF: ", net_difference); 

        if(position.z > .01):
            net_error = tof_difference/position.z; 
            print("Error%: ", net_error); 


        

        
    

    

    