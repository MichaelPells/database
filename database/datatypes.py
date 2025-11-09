from database.variables import *
import database.primitives as primitives

class Data:
    def __init__(self, check=None, exceptions=None, cast=None):
        if check != None:
            self.check = check

        if cast != None:
            self.cast = cast

        if exceptions != None:
            self.exceptions = exceptions

    def check(self, data):
        return True

    def validate(self, data):
        if self.check(data):
            return [self]
        else:
            raise Exception
    
    def allow(self, data, exceptions):
        if type(data) not in exceptions:
            raise Exception

    def cast(self, data):
        return data
    
    exceptions = [primitives.null, primitives.error]


Any = Data()
Number = Data(lambda data: isinstance(data, int))
String = Data(lambda data: isinstance(data, str))
        
class Option(Data):
    options = [Null()]

    def validate(data):
        if data in Option.options:
            return True
        else:
            return False
    
class Date(Data):
    ...

class Time(Data):
    ...

class DateTime(Data):
    ...

class Telephone(Data):
    ...

class Email(Data):
    ...

class List(Data):
    ...

class Object(Data):
    ...

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