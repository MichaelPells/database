from database.variables import *
import database.primitives as primitives

class Data:
    def __init__(self, validate=None, exceptions=None, cast=None):
        if validate != None:
            self.validate = validate

        if cast != None:
            self.cast = cast

        if exceptions != None:
            self.exceptions = exceptions

    def validate(data):
        return [Data]
    
    def allow(data, exceptions):
        if type(data) not in exceptions:
            raise Exception

    def cast(data):
        return data
    
    exceptions = [primitives.null, primitives.error]


class Any(Data):
    ...


def validate(data):
    if isinstance(data, int):
        return [Number]
    else:
        raise Exception

def cast(data):
    result = int(data)
    return result

Number = Data(validate, cast)

# class Number(Data):
#     def validate(data):
#         if isinstance(data, int):
#             return [Number]
#         else:
#             raise Exception

#     def cast(data):
#         result = int(data)
#         return result

class String(Data):
    def validate(data):
        if isinstance(data, str):
            return [String]
        else:
            raise Exception
        
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