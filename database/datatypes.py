from database.variables import *

class Data:
    def check(data):
        return True
    
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
