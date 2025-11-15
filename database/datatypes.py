from database.variables import *
import database.primitives as primitives

class Data:
    def __init__(self, rule=None, cast=None, exceptions=None, **build):
        self.prototypes = []
        self.rules = [rule] if rule else []
        self.casts = [cast] if cast else []
        self.exceptions = exceptions or [primitives.null, primitives.error]

        self.builds = []
        for name, obj in build.items():
            self.__setattr__(name, obj)
            self.builds.append(name)

    def __call__(self, newrule=None, rule=None, newcast=None, cast=None, exceptions=None, **build):
        exceptions = exceptions or self.exceptions
        build = {**{name: self.__getattribute__(name) for name in self.builds}, **build}

        subtype = Data(
            exceptions=exceptions,
            **build)

        subtype.rules = self.rules
        if newrule: subtype.rules.append(newrule)
        if rule: subtype.rules = [rule]

        subtype.casts = self.casts
        if newcast: subtype.rules.append(newcast)
        if cast: subtype.casts = [cast]

        subtype.prototypes.append(self)

        return subtype
    
    def validate(self, data):
        if not False in [rule(data, self) for rule in self.rules] or type(data) in self.exceptions:
            return [self]
        else:
            raise Exception
        
    def sanitize(self, data):
        if type(data) not in self.exceptions:
            for cast in self.casts:
                data = cast(data)

        return data


Any = Data()

Number = Data(
    rule=lambda data, Type: isinstance(data, int)
    )

String = Data(
    rule=lambda data, Type: isinstance(data, str)
    )

Option = Data(
    rule=lambda data, Type: data in Type.options,
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