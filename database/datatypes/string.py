from .data import *

String = Data(
    rule=lambda data, Type: isinstance(data, str), name="String"
    )
