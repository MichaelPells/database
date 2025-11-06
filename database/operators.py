class Gate:
    def __init__(self, *operands):
        self.operands = operands

class AND(Gate):
    def select(self, results, table, database):
        return set(results[0]).intersection(*results[1:])
    
    def validate(self, data):
        compatibles = []

        for operand in self.operands:
            try:
                compatibles.extend(operand.validate(data))
            except Exception:
                raise Exception
            
        return compatibles

class OR(Gate):
    def select(self, results, table, database):
        return set(results[0]).union(*results[1:])
    
    def validate(self, data):
        for operand in self.operands:
            try:
                return operand.validate(data)
            except Exception:
                pass

        raise Exception

class NOT(Gate):
    def select(self, results, table, database):
        superset = database.tables[table]['entries'].keys()
        return set(superset).difference(results[0])

    def validate(self, data):
        try:
            self.operands[0].validate(data)
        except Exception:
            return []
        
        raise Exception

        
