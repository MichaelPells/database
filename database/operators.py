class Gate:
    def __init__(self, *operands):
        self.operands = operands

class AND(Gate):
    def select(self, results, table, database):
        return set(results[0]).intersection(*results[1:])
    
    def validate(self, validities):
        return not False in validities

class OR(Gate):
    def select(self, results, table, database):
        return set(results[0]).union(*results[1:])
    
    def validate(self, validities):
        return True in validities

class NOT(Gate):
    def select(self, results, table, database):
        superset = database.tables[table]['entries'].keys()
        return set(superset).difference(results[0])

    def validate(self, validities):
        return not validities[0]
