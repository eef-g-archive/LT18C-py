from enum import Enum
from Modules.Core.LT18C import DroneController
from Modules.Core.Vectors import Vector3

MAX_STORAGE_SIZE = 1024; 

class Type(Enum):
    Move = 0
    Rotate = 1 

class Record(object):  
    def __init__(self, controller):
        self.list = []; 
        self.coordinate_records = []; 
        self.controller:DroneController = controller; 

    @staticmethod
    def instantiate(controller):
        global record_instance; 
        record_instance = Record(controller);  

    @staticmethod
    def __get_instance():
        global record_instance; 
        return record_instance; 

    @staticmethod
    def get_list():
        return Record.__get_instance().list; 

    @staticmethod
    def get_coordinate_records():
        return Record.__get_instance().coordinate_records; 

    @staticmethod
    def record_movement(position: Vector3):
        Record.__get_instance().list.append((Type.Move, position)); 
    
    @staticmethod
    def record_position(position: Vector3):
        Record.__get_instance().coordinate_records.append((Type.Move, position)); 

    @staticmethod
    def record_rotation(rotation: Vector3):
        Record.__get_instance().list.append((Type.Rotate, rotation)); 

def record_position(controller, position):
    Record.record_position(position); 

def record_movement(controller, newPosition):
    Record.record_movement(newPosition); 

def record_rotation(controller, newRotation):
    Record.record_rotation(newRotation); 

def instantiate(controller):
    Record.instantiate(controller); 
    
    controller.motor_controller.add_movement_invoke(record_movement); 
    controller.motor_controller.add_rotation_invoke(record_rotation); 

def print_record():
    for item in Record.get_list():
        print(item[0], str(item[1])); 
    
