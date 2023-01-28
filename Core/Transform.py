import math
from Core.Vectors import Vector3 

class Transform():
    def __init__(self, controller):
        self.controller = controller; 
        self.position = Vector3(0, 0, 0); 

        # pitch, yaw, roll. We're using this since we shouldn't have to rotate three at a time. 
        #   If we do then we'll have to use Quaternions to prevent gimbal lock. 
        self.rotation = Vector3(0, 0, 0); 

    @property
    def forward(self):
        x =  math.cos(self.rotation.x) * math.sin(self.rotation.y); 
        y = -math.sin(self.rotation.x); 
        z =  math.cos(self.rotation.x) * math.cos(self.rotation.y); 
        return Vector3(x, y, z); 
        
    @property
    def right(self): 
        x =  math.cos(self.rotation.y); 
        y =  0; 
        z = -math.sin(self.rotation.y); 
        return Vector3(x, y, z); 

    @property
    def up(self):
        x = math.sin(self.rotation.x) * math.sin(self.rotation.y); 
        y = math.cos(self.rotation.x); 
        z = math.sin(self.rotation.x) * math.cos(self.rotation.y); 
        return Vector3(x, y, z); 

    def look_at(self, other:Vector3, apply = False) -> Vector3:
        dir:Vector3 = (self.position - other).normalized; 
        degree = math.tan(dir.x / dir.y); 
        
        if apply: self.rotation.y = degree; 
        return Vector3(self.rotation.x, degree, self.rotation.z); 

