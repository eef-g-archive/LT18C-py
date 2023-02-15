import math
class Vector3():
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.x = x; 
        self.y = y; 
        self.z = z; 

    def __add__(self, __o):
        if isinstance(__o, (float, int)):
            x = self.x + __o; 
            y = self.y + __o; 
            z = self.z + __o; 
        elif isinstance(__o, Vector3):
            x = self.x + __o.x; 
            y = self.y + __o.y; 
            z = self.z + __o.z; 
        else:
            raise Exception("An object type of Vector3 cannot be added with the type of " + str(__o.type));   
        return Vector3(x, y, z); 
    def __sub__(self, __o:object):
        if isinstance(__o, (float, int)):
            x = self.x - __o; 
            y = self.y - __o; 
            z = self.z - __o; 
        elif isinstance(__o, Vector3):
            x = self.x - __o.x; 
            y = self.y - __o.y; 
            z = self.z - __o.z; 
        else:
            raise Exception("An object type of Vector3 cannot be subtracted with the type of " + str(__o.type));   
        return Vector3(x, y, z);  
    def __mul__(self, __o):
        if isinstance(__o, (float, int)):
            x = self.x * __o; 
            y = self.y * __o; 
            z = self.z * __o; 
        elif isinstance(__o, Vector3):
            x = self.x * __o.x; 
            y = self.y * __o.y; 
            z = self.z * __o.z; 
        else:
            raise Exception("An object type of Vector3 cannot be multiplied with the type of " + str(__o.type));   
        return Vector3(x, y, z);  
    def __div__(self, __o):
        if isinstance(__o, (float, int)):
            x = self.x / __o; 
            y = self.y / __o; 
            z = self.z / __o; 
        elif isinstance(__o, Vector3):
            x = self.x / __o.x; 
            y = self.y / __o.y; 
            z = self.z / __o.z; 
        else:
            raise Exception("An object type of Vector3 cannot be divided with the type of " + str(__o.type));   
        return Vector3(x, y, z);  
    
    def __eq__(self, __o: object) -> bool: 
        if(self.x != __o.x or
            self.y != __o.y or
            self.z != __o.z): 
            return False; 
        return True;  

    def __ne__(self, __o: object) -> bool:  
        if(__o == None):
            return self == __o; 
        if(self.x == __o.x or
            self.y == __o.y or
            self.z == __o.z): 
            return False; 
        return True;  
 
    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z); 
    def __iadd__(self, __o):
        return self.__add__(__o); 
    def __idiv__(self, __o):
        return self.__div__(__o); 
    def __imul__(self, __o):
        return self.__mul__(__o); 
    def __isub__(self, __o):
        return self.__sub__(__o); 
    def __pow__(self, __o):
        return Vector3(self.x ** __o, self.y ** __o, self.z ** __o); 
    def __abs__(self):
        return Vector3(abs(self.x), abs(self.y), abs(self.z)); 
    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"; 
    def __int__(self):
        return Vector3(int(self.x), int(self.y), int(self.z)); 
    def __round__(self):
        return Vector3(round(self.x), round(self.y), round(self.z)); 

    def distance(self, other):
        return Vector3.Distance(self, other); 

    @staticmethod
    def Distance(p1, p2): 
        return math.sqrt(((p2.x - p1.x) ** 2  + (p2.y - p1.y) ** 2 + (p2.z - p1.z) ** 2)); 

    @property
    def magnitude(self):
        return self.distance(Vector3(0, 0, 0)); 

    @staticmethod
    def Zero():
        return Vector3(0, 0, 0); 


    @property
    def normalized(self):
        if(self.x == 0 and self.y == 0 and self.z == 0):
            return Vector3.Zero(); 

        return self.__div__(self.magnitude) 

    @property
    def to_unity(self): 
        return Vector3(self.y, self.z, self.x)
        
    def is_directional(self):
        zero_count = 0; 
        if self.x == 0: zero_count += 1; 
        if self.y == 0: zero_count += 1; 
        if self.z == 0: zero_count += 1; 
        return zero_count >= 2; 
    
    def to_list(self):
        return [self.x, self.y, self.z]; 
 
