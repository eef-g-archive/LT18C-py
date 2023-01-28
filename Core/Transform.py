import math
from Core.Vectors import Vector3 

class Transform():
    def __init__(self):
        self.position = Vector3(0, 0, 0); 
        # pitch, yaw, roll. We're using this since we shouldn't have to rotate three at a time. 
        #   If we do then we'll have to use Quaternions to prevent gimbal lock. 
        self.rotation = Vector3(0, 0, 0); 

    @property
    def forward(self):
        y =  math.cos(self.rotation.x) * math.sin(self.rotation.y); 
        z = -math.sin(self.rotation.x); 
        x =  math.cos(self.rotation.x) * math.cos(self.rotation.y); 
        return Vector3(x, y, z); 
        
    @property
    def right(self): 
        # x y z -> y z x
        y =  math.cos(self.rotation.y); 
        z =  0; 
        x = -math.sin(self.rotation.y); 
        return Vector3(x, y, z); 

    @property
    def up(self):
        y = math.sin(self.rotation.x) * math.sin(self.rotation.y); 
        z = math.cos(self.rotation.x); 
        x = math.sin(self.rotation.x) * math.cos(self.rotation.y); 
        return Vector3(x, y, z); 

    def look_at(self, other:Vector3, apply = False) -> Vector3:     
        
        print("\npos: ", self.position); 
        print("other: ", other);        

        difference = self.position - other; 
        print("difference: ", difference);  

        dir:Vector3 = difference.normalized.to_unity;  

        print("dir: ", dir); 
        degree = math.degrees(math.tan(dir.z / dir.x));  
        
        print("degree: ", degree, "\n"); 
        
        if apply: self.rotation.y = degree; 
        return Vector3(self.rotation.x, degree, self.rotation.z); 

