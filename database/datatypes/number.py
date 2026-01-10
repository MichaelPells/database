from .data import *

Number = Data(
    rule=lambda data, Type: isinstance(data, int), name="Number"
    )
