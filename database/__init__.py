import threading
import copy

from database.datatypes import *
from database.variables import *
from database.idioms import *
from database.operators import *
from database.errors import *
import database.primitives as primitives


class Result:
    def __init__(self, rows=[], database=None):
        self.rows = list(rows)
        self.database = database

        self.count = len(self.rows)

    def __len__(self):
        return self.count

    def get(self, row: list | AnyOf = None, column: list | set | AnyOf = Null(), table = None):
        table = table or self.database.primarytable
        Table = self.database.tables[table]
        row = row if row != None else range(0, self.count)
        column = column or set(Table['columns'].keys())

        if type(row) == list or type(row) == range:
            entries = []
            for i in row:
                index = self.rows[i]
                entry = Table['entries'][index]
                if type(column) == list:
                    record = []
                    for col in column:
                        offset = Table['columns'][col]['offset']
                        field = entry[offset]
                        record.append(field)
                elif type(column) == set:
                    record = {}
                    for col in column:
                        offset = Table['columns'][col]['offset']
                        field = entry[offset]
                        record[col] = field
                else:
                    offset = Table['columns'][column]['offset']
                    record = entry[offset] # field

                entries.append(record)

            result = entries
        else:
            index = self.rows[row]
            entry = Table['entries'][index]

            if type(column) == list:
                result = [] # record
                for col in column:
                    offset = Table['columns'][col]['offset']
                    field = entry[offset]
                    result.append(field)
            elif type(column) == set:
                result = {} # record
                for col in column:
                    offset = Table['columns'][col]['offset']
                    field = entry[offset]
                    result[col] = field
            else:
                offset = Table['columns'][column]['offset']
                result = entry[offset] # field
        
        return result

    def sort(self, column, order):
        return self


class Database:
    def __init__(self):
        self.lock = threading.Lock()

        self.tables = {}
        self.primarytable = None
        self.backups = []
        self.recenttables = []

    def _buildindex(self, table, rows=Result(), columns=[]):
        Table = self.tables[table]
        columns = columns or list(Table['columns'].keys())
        entries = Table['entries']
        indexes = Table['indexes']
        references = Table['references']

        for column in columns:
            if column not in indexes:
                indexes[column] = {}

        rows = rows.rows or list(Table['entries'].keys())

        order = []
        allsources = {}

        def register(rows, columns, sources):
            for index in rows:
                for column in columns:
                    if column not in allsources:
                        allsources[column] = {}

                    if index not in allsources[column]:
                        allsources[column][index] = []

                    allsources[column][index].extend(sources)
                    order.append((index, column))


        register(rows, columns, ())

        n = 0
        while True:
            n += 1

            try:
                index, column = order.pop()
            except IndexError:
                break

            try:
                allsources[column][index]
            except KeyError:
                continue

            offset = Table['columns'][column]['offset']
            row = entries[index]
            field = row[offset]
            sources = allsources[column][index]

            del allsources[column][index]

            if not allsources[column]:
                del allsources[column]

            if not isinstance(field, Var):
                try:
                    field = self._validate(table, column, field)
                except IncompatibleTypesError as e:
                    raise IncompatibleTypesError((index, column, e.args[0]))

                if field not in indexes[column]:
                    indexes[column][field] = {}

                indexes[column][field][index] = index
            else:
                for source in sources:
                    if source and (source[0] == index or source[0] == "*") and source[1] == column:
                        raise CyclicReferencingError((index, column, field))

                field.index(self, table, Params(indexes=indexes, column=column, index=index))
            
            # Rebuild index for its dependent variables in references (affected fields):
            if index in references[column]:
                cols = references[column][index]

                for col, rs in list(cols.items()):
                    rs = list(rs)
                    self._clearindex(table, Result(rs, self), [col])
                    try:
                        register(rs, [col], sources if sources else [(index, column)])
                    except IncompatibleTypesError as e:
                        raise InapplicableValueError((index, column, e.args[0][0], e.args[0][1], e.args[0][2]))
                    except InapplicableValueError as e:
                        raise InapplicableValueError((index, column, e.args[0][2], e.args[0][3], e.args[0][4]))

            if '*' in references[column]:
                cols = references[column]['*']

                for col, rs in list(cols.items()):
                    rs = list(rs)
                    self._clearindex(table, Result(rs, self), [col])
                    try:
                        register(rs, [col], sources if sources else [(index, column)])
                    except IncompatibleTypesError as e:
                        raise InapplicableValueError((index, column, e.args[0][0], e.args[0][1], e.args[0][2]))
                    except InapplicableValueError as e:
                        raise InapplicableValueError((index, column, e.args[0][2], e.args[0][3], e.args[0][4]))

        if n >= 1000:
            print(f'Warning: Too long iteration ({n}) for {(self._identify(table, index), column)}')

    def _clearindex(self, table, rows=Result(), columns=[]):
        Table = self.tables[table]
        columns = {column: Table['columns'][column]['offset'] for column in columns} or Table['columns']
        entries = Table['entries']
        indexes = Table['indexes']

        rows = rows.rows or list(Table['entries'].keys())

        for index in rows:
            for column, offset in columns.items():
                try:
                    row = entries[index]
                    field = row[offset]

                    if not isinstance(field, Var):
                        del Table['indexes'][column][field][index]
                        if not Table['indexes'][column][field]:
                            del Table['indexes'][column][field]
                    else:
                        field.unindex(self, table, Params(indexes=indexes, column=column, index=index))
                except:
                    pass

    def _select(self, table, column=None, value=None): # What should really be the defaults here?
        Column = self.tables[table]['indexes'][column]

        if not isinstance(value, Var):
            if value not in Column:
                return []
            else:
                return list(Column[value].keys())
        elif isinstance(value, Const):
            value = value.compute()

            if value not in Column:
                return []
            else:
                return list(Column[value].keys())
        else:
            return value.process(self, table, Params(column=column))

    def _selector(self, table, query):
        if type(query) == list:
            return query
        
        if type(query) == dict:
            column, value = list(query.items())[0]
            return self._select(table=table, column=column, value=value)
        
        if isinstance(query, Gate):
            results = []

            for operand in query.operands:
                if type(operand) == dict:
                    queries = operand

                    for column, value in queries.items():
                        results.append(self._select(table=table, column=column, value=value))
                else:
                    results.append(self._selector(table, operand))

            return query.select(results, table, self)
        
    def _identify(self, table, index):
        Table = self.tables[table]

        primarykey = Table['primarykey']
        offset = Table['columns'][primarykey]['offset']

        return Table['entries'][index][offset]

    def _validate(self, table, column, data):
        Table = self.tables[table]

        type = Table['columns'][column]['type']
        valid = type.check(data)

        if valid:
            return type.cast(data)
        elif type.allow(data, type.exceptions):
            return data
        else:
            raise IncompatibleTypesError(f'{data} is not of {column} type - {type.__name__}')

    def create(self, table=None, columns=[], entries=[], primarykey=None, primary=False): # What happens when entries contain dependent variables?
        with self.lock:
            table = table or self.primarytable

            def undo():
                del self.tables[table]

                if self.primarytable == table:
                    self.primarytable = None

            self.backups.append(undo)

            references = {column[0] if type(column) == tuple else column: {} for column in columns}
            columns = {
                column[0] if type(column) == tuple else column: {
                    'offset': offset,
                    'type': column[1] if type(column) == tuple else Any
                }
                for offset, column in enumerate(columns)
            }

            self.tables[table] = {
                'columns': columns,
                'entries': {},
                'references': references,
                'indexes': {},
                'count': 0,
                'nextindex': 1,
                'primarykey': primarykey
            }

            if primary or not self.primarytable:
                self.primarytable = table

            Table = self.tables[table]

            for entry in entries:
                for column in Table['columns']:
                    offset = Table['columns'][column]['offset']

                    if isinstance(entry[offset], Idiom):
                        entry[offset] = entry[offset].decode(locals())

            entries = {(index + 1): entry for index, entry in enumerate(entries)}

            Table['entries'].update(entries)
            Table['count'] += len(entries)
            Table['nextindex'] += len(entries)

            try:
                self._buildindex(table)
            except IncompatibleTypesError as e:
                self.undo()
                e.args = (f'{e.args[0][1]} cannot be updated for entry {self._identify(table, e.args[0][0])}. {e.args[0][2]}',)
                raise
            except InapplicableValueError as e:
                self.undo()
                e.args = (f'{e.args[0][1]} cannot be updated for entry {self._identify(table, e.args[0][0])}. Results in IncompatibleTypesError for {e.args[0][3]} of entry {self._identify(table, e.args[0][2])}. {e.args[0][4]}',)
                raise
            except CyclicReferencingError as e:
                self.undo()
                e.args = (f'{e.args[0][1]} cannot be updated for entry {self._identify(table, e.args[0][0])}. {e.args[0][2]} references self.',)
                raise

    def read(self, table=None, rows=None):
        with self.lock:
            table = table or self.primarytable

            Table = self.tables[table]

            if rows == None:
                rows = list(Table['entries'].keys())
            else:
                rows = self._selector(table, rows)

            result = Result(rows, self)

            return result

    def view(self, table=None, rows=None):
        with self.lock:
            table = table or self.primarytable

            Table = self.tables[table]

            if rows == None:
                rows = list(Table['entries'].keys())
            else:
                rows = self._selector(table, rows)

            result = []

            for index in rows:
                result.append(Table['entries'][index])

            return result

    def update(self, table=None, rows=None, record={}):
        with self.lock:
            table = table or self.primarytable

            Table = self.tables[table]

            if rows == None:
                rows = list(Table['entries'].keys())
            else:
                rows = self._selector(table, rows)
    
            columns = record.keys()

            oldvalues = {}

            for column in record:
                oldvalues[column] = {}
                offset = Table['columns'][column]['offset']

                for index in rows:
                    oldvalues[column][index] = copy.copy(Table['entries'][index])[offset]

            def undo():
                self._clearindex(table, Result(rows, self), columns)

                for column in oldvalues:
                    offset = Table['columns'][column]['offset']

                    for index in rows:
                        Table['entries'][index][offset] = oldvalues[column][index]

                self._buildindex(table, Result(rows, self), columns)

            self.backups.append(undo)

            self._clearindex(table, Result(rows, self), columns)

            for column, value in record.items():
                offset = Table['columns'][column]['offset']

                for index in rows:
                    if not isinstance(value, Idiom):
                        Table['entries'][index][offset] = value
                    else:
                        Table['entries'][index][offset] = value.decode(locals())

            try:
                self._buildindex(table, Result(rows, self), columns)
            except IncompatibleTypesError as e:
                self.undo()
                e.args = (f'{e.args[0][1]} cannot be updated for entry {self._identify(table, e.args[0][0])}. {e.args[0][2]}',)
                raise
            except InapplicableValueError as e:
                self.undo()
                e.args = (f'{e.args[0][1]} cannot be updated for entry {self._identify(table, e.args[0][0])}. Results in IncompatibleTypesError for {e.args[0][3]} of entry {self._identify(table, e.args[0][2])}. {e.args[0][4]}',)
                raise
            except CyclicReferencingError as e:
                self.undo()
                e.args = (f'{e.args[0][1]} cannot be updated for entry {self._identify(table, e.args[0][0])}. {e.args[0][2]} references self.',)
                raise

    def insert(self, table=None, entries=[]):
        with self.lock:
            table = table or self.primarytable

            Table = self.tables[table]

            for entry in entries:
                for column in Table['columns']:
                    offset = Table['columns'][column]['offset']

                    if isinstance(entry[offset], Idiom):
                        entry[offset] = entry[offset].decode(locals())

            start = Table['nextindex']
            stop = start + len(entries)
            rows = range(start, stop)
            entries = {(start + index): entry for index, entry in enumerate(entries)}

            Table['entries'].update(entries)
            Table['count'] += len(entries)
            Table['nextindex'] = stop

            newindexes = [(start + index) for index in range(len(entries))]

            def undo():
                self._clearindex(table, Result(rows, self))
                for index in newindexes:
                    del Table['entries'][index]

            self.backups.append(undo)

            try:
                self._buildindex(table, Result(rows, self))
            except IncompatibleTypesError as e:
                self.undo()
                e.args = (f'{e.args[0][1]} cannot be updated for entry {self._identify(table, e.args[0][0])}. {e.args[0][2]}',)
                raise
            except InapplicableValueError as e:
                self.undo()
                e.args = (f'{e.args[0][1]} cannot be updated for entry {self._identify(table, e.args[0][0])}. Results in IncompatibleTypesError for {e.args[0][3]} of entry {self._identify(table, e.args[0][2])}. {e.args[0][4]}',)
                raise
            except CyclicReferencingError as e:
                self.undo()
                e.args = (f'{e.args[0][1]} cannot be updated for entry {self._identify(table, e.args[0][0])}. {e.args[0][2]} references self.',)
                raise

    def delete(self, table=None):
        with self.lock:
            table = table or self.primarytable

            Table = self.tables[table]

            if self.primarytable == table:
                primary = True

            oldTable = copy.copy(Table)

            def undo():
                self.tables[table] = oldTable

                if primary:
                    self.primarytable = table

            self.backups.append(undo)

            del self.tables[table]

            if primary:
                self.primarytable = None

    def remove(self, table=None, rows=None):
        with self.lock:
            table = table or self.primarytable

            Table = self.tables[table]

            if rows == None:
                rows = list(Table['entries'].keys())
            else:
                rows = self._selector(table, rows)

            entries = {}

            for index in rows:
                entries[index] = copy.copy(Table['entries'][index])

            def undo():
                Table['entries'].update(entries)

                self._buildindex(table, Result(rows, self))

            self.backups.append(undo)

            self._clearindex(table, Result(rows, self))

            for index in rows:
                del Table['entries'][index]

            Table['count'] -= len(rows)

    def undo(self, changes=1):
        if changes <= len(self.backups):
            if changes == 1:
                return self.backups.pop()()
            else:
                return [self.backups.pop()() for change in range(changes)]
        else:
            raise Exception

