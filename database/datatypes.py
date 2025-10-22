from database.variables import *
from database.primitives import *

class Data:
    exceptions = [null, error] # Is `Error()` correct and working??

    def check(data):
        return True
    
    def allow(data, exceptions):
        if type(data) in exceptions:
            return True
        else:
            return False

    def cast(data):
        return data

class Number(Data):
    def check(data):
        if isinstance(data, int):
            return True
        else:
            return False

    def cast(data):
        result = int(data)
        return result

class String(Data):
    def check(data):
        if isinstance(data, str):
            return True
        else:
            return False
        
class Option(Data):
    options = [Null()]

    def check(data):
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

class Any(Data):
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