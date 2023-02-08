import math 
from Modules.Core.Vectors import Vector3 

class Transform():
    def __init__(self):
        self.position = Vector3(0, 0, 0);  
        self.rotation = Vector3(0, 0, 0); 

    @property
    def pitch(self):
        return math.radians(self.rotation.x); 
    @property
    def yaw(self):
        return math.radians(self.rotation.y); 
    @property
    def roll(self):
        return math.radians(self.rotation.z); 

    @property
    def forward(self):  
        x =  math.cos(self.pitch) * math.sin(self.yaw); 
        y = -math.sin(self.pitch); 
        z =  math.cos(self.pitch) * math.cos(self.yaw);  
        return Vector3(x, y, z);  
    @property
    def right(self):   
        x =  math.cos(self.yaw); 
        y =  0; 
        z = -math.sin(self.yaw); 
        return Vector3(x, y, z); 
    @property
    def up(self):  
        x = math.sin(self.pitch) * math.sin(self.yaw); 
        y = math.cos(self.pitch); 
        z = math.sin(self.pitch) * math.cos(self.yaw); 

        return Vector3(x, y, z);  

    def look_at(self, other:Vector3) -> Vector3:    

        difference = other - self.position;   
        direction:Vector3 = difference.normalized;  

        degree = math.degrees(math.atan2(direction.x, direction.z));    

        print("degree: ", degree, "dir: ", direction, "\n");  
        
        return Vector3(self.rotation.x, degree, self.rotation.z); 
