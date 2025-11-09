from database.variables import *
import database.primitives as primitives

class Data:
    def __init__(self, check=None, exceptions=None, cast=None, **build):
        if check != None:
            self.check = check

        if cast != None:
            self.cast = cast

        if exceptions != None:
            self.exceptions = exceptions

        for name, obj in build.items():
            self.__setattr__(name, obj)

    def __call__(self, check=None, exceptions=None, cast=None, **build):
        check = check or self.check
        exceptions = exceptions or self.exceptions
        cast = cast or self.cast

        return Data(check, exceptions, cast, **build)

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
Option = Data(lambda data: data in Option.options,
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