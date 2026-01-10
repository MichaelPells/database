from .data import *

Option = Data(
    rule=lambda data, Type: data in Type.options, name="Option",
    options = [] # Null()
    )
