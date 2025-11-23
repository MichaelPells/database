class Compound:
    def __init__(self, *operands):
        self.operands = operands

    def __iter__(self):
        for operand in self.operands:
            yield operand

class AND(Compound):
    def select(self, results, table, database):
        return set(results[0]).intersection(*results[1:])
    
    def validate(self, data):
        compatibles = []

        for operand in self:
            try:
                compatibles.extend(operand.validate(data))
            except Exception:
                raise Exception
            
        return compatibles

class OR(Compound):
    def select(self, results, table, database):
        return set(results[0]).union(*results[1:])
    
    def validate(self, data):
        for operand in self:
            try:
                return operand.validate(data)
            except Exception:
                pass

        raise Exception

class NOT(Compound):
    def select(self, results, table, database):
        superset = database.tables[table]['entries'].keys()
        return set(superset).difference(results[0])

    def validate(self, data):
        try:
            self.operands[0].validate(data)
        except Exception:
            return []
        
        raise Exception

        
