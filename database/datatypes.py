from database.variables import *
import database.primitives as primitives

class Data:
    def __init__(self, rule=None, cast=None, exceptions=None, **build):
        self.prototypes = []
        self.rules = [rule] if rule else []
        if cast: self.cast = cast
        self.exceptions = exceptions or [primitives.null, primitives.error]

        self.builds = []
        for name, obj in build.items():
            self.__setattr__(name, obj)
            self.builds.append(name)

    def __call__(self, newrule=None, rule=None, cast=None, exceptions=None, **build):
        cast = cast or self.cast
        exceptions = exceptions or self.exceptions
        build = {**{name: self.__getattribute__(name) for name in self.builds}, **build}

        subtype = Data(
            cast=cast,
            exceptions=exceptions,
            **build)

        if newrule != None: subtype.rules.append(newrule)
        if rule != None: subtype.rules = [rule]
        subtype.prototypes.append(self)

        return subtype
    
    def validate(self, data):
        if not False in [rule(data, self) for rule in self.rules] or type(data) in self.exceptions:
            return [self]
        else:
            raise Exception
        
    def sanitize(self, data):
        if type(data) not in self.exceptions:
            data = self.cast(data)

        return data

    def cast(self, data):
        return data


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