from database.variables import *
import database.primitives as primitives

class Data:
    def __init__(self, check=None, cast=None, exceptions=None, **build):
        if check != None:
            self.check = check

        if cast != None:
            self.cast = cast

        if exceptions != None:
            self.exceptions = exceptions

        for name, obj in build.items():
            self.__setattr__(name, obj)

    def __call__(self, check=None, cast=None, exceptions=None, **build):
        check = check or self.check
        cast = cast or self.cast
        exceptions = exceptions or self.exceptions

        return Data(check, cast, exceptions, **build)
    
    def validate(self, data):
        if self.check(data, self) or type(data) in self.exceptions:
            return [self]
        else:
            raise Exception
        
    def sanitize(self, data):
        if type(data) not in self.exceptions:
            data = self.cast(data)

        return data

    def check(self, data, Type):
        return True

    def cast(self, data):
        return data
    
    exceptions = [primitives.null, primitives.error]


Any = Data()
Number = Data(lambda data, Type: isinstance(data, int))
String = Data(lambda data, Type: isinstance(data, str))
Option = Data(lambda data, Type: data in Type.options,
              options = [Null()]
              )
Date = Data()
Time = Data()
DateTime = Data()
Telephone = Data()
Email = Data()
List = Data()
Object = Data()

# Possible future types:
# - File
# - Binary
# - Image
# - Colour
# - Fraction
# - Percentage
# - Degree
# - Integer
# - Decimal
# - Range

# The above will extend each other.