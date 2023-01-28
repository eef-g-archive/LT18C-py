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
        return Vector3(abs(self.x), abs(self.y), abs(self.y)); 
    def __str__(self):
        return "Vector3(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"; 

    def distance(self, other):
        return Vector3.Distance(self, other); 

    @staticmethod
    def Distance(p1, p2): 
        return ((p1.x - p2.x) ** 2  + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2) ** .5; 

    @property
    def magnitude(self):
        return self.distance(Vector3(0, 0, 0)); 

    @property
    def normalized(self):
        return self.__div__(self.magnitude); 

    @property
    def to_unity(self): 
        return Vector3(self.y, self.z, self.x); 
        
