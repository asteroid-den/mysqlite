# MySQLite

Minimalistic MySQL and SQLite 3 ORM  

## Quickstart

> SQLite 3
```python3
from mysqlite import *
db = DB(filename = 'test.db')
db.create_table('users', {'id': 'INT NOT NULL', 'balance': 'FLOAT NOT NULL DEFAULT 50'})
db.insert('users', {'id': 1})
db.insert('users', {'id': 2, 'balance': 100})
print(db.select('users'))
```
Output:
```pycon
+----+---------+
| id | balance |
+----+---------+
| 1  |    50   |
+----+---------+
| 2  |   100   |
+----+---------+
```

> MySQL
```python3
from mysqlite import DB
from config import DB_NAME, USER, PASSWORD
db = DB(DB_NAME, USER, PASSWORD, table = 'pets')
result = db.select(['id', 'name'])
for pet in result:
    print(f'Pet ID: {pet.id}; Pet name: {pet.name}')

# Pet ID: 1; Pet name: Dixie
# Pet ID: 2; Pet name: Walter
# Pet ID: 3; Pet name: Odie
```  
## Docs

#### `class mysqlite.DB(db_name=None, user='root', passwd=None, filename=None, table=None)`
Main class to interact with DBs. Only `db_name` + `passwd` + `user` (user is optional) for connecting to MySQL DB **or** `filename` for connectiong to SQLite3 DB must be provided. You can specify a `table` if you want not to specify it in every request.  
#### `create_table(name, fields)`
**Parameters**:
- **name**(`str`) — a name of new table
- **fields**(`dict`|`str`) — description of columns. Must be provided as dictionary, where keys are column names and values are characteristics of this column, or as a total description of all columns in a single string **without opening and closing parantheses**.

Returns `True` on success, otherwise throws error of libraries-connectors.  
#### `insert(table, dic, **kwargs)`
**Parameters**:
- **table**(`str`, _optional_) — name of table to insert values. Can be omitted, if table was specified when created `mysqlite.DB` instance.
- **dic**(`dict`, _optional_) — dictionary with values to insert, where keys are column names, and values are values to insert.
**dic** **_can be omitted_** if you specify values as keyword arguments. So,
```python3
db.insert('users', {'id': 1, 'balance': 50})
```
is the same as
```python3
db.insert('users', id = 1, balance = 50)
```

Returns `True` on success, otherwise throws error of libraries-connectors.  
#### `select(table, args_list, where, order_by, group_by, limit)`
**Parameters**:
- **table**(`str`, _optional_) — name of table to retrieve values. Can be omitted, if table was specified when created `mysqlite.DB` instance.
- **args_list**(`list`|`str`, _optional_) — column names from which values will be retrived. Can be `str`, if only 1 column needed, or `list`, if few columns needed. Defaults to **mysqlite.ALL**. Can be ommited if you want to use default value or if you 
- **where**(`str`|`dict`, _optional_) — condition, that filters values from table. Can be provided as dictionary, where keys are column names and values are conditions, or as a total condition in a single string.
- **order_by**(`list`|`str`, _optional_) — sorting of a result ascending or descending. Can be a `list` containing names of columns and ASC/DESC if needed, or `str` with total order rule.
- **group_by**(`str`, _optional_) — used to group result by specific column.
- **limit**(`int`, _optional_) — used to limit the amount of records that goes to result.

Returns **mysqlite.Response** object containing result of query.  
#### `update(table, dic, where, **kwargs)`
**Parameters**:
- **table**(`str`, _optional_) — name of table to update values. Can be omitted, if table was specified when created `mysqlite.DB` instance.
- **dic**(`dict`, _optional_) — dictionary with values to insert, where keys are column names, and values are values to insert.
**dic** **_can be omitted_** if you specify values as keyword arguments. So,
```python3
db.update('users', {'balance': 50})
```
is the same as
```python3
db.update('users', balance = 50)
```
- **where**(`str`|`dict`, _optional_) — condition, that filters values from table. Can be provided as dictionary, where keys are column names and values are conditions, or as a total condition in a single string.
**_Do not_** use **update()** method without specifying this parameter in most cases, because in this case you'll change **_ALL_** records. Results of processing SQL queries are irreversible, so you can lose some data.

Returns `True` on success, otherwise throws error of libraries-connectors.  
#### `delete(table, where)`
**Parameters**:
- **table**(`str`, _optional_) — name of table to delete values. Can be omitted, if table was specified when created `mysqlite.DB` instance.
- **where**(`str`|`dict`, _optional_) — condition, that filters values from table. Can be provided as dictionary, where keys are column names and values are conditions, or as a total condition in a single string.
**_Do not_** use **delete()** method without specifying this parameter in most cases, because in this case you'll delete **_ALL_** records. Results of processing SQL queries are irreversible, so you can lose some data.

Returns `True` on success, otherwise throws error of libraries-connectors.  
#### `raw_select(query, tup_res)`
This method can be used if `select()` does not provide enough functionality.  
**Parameters**:
- **query**(`str`) — string containing completed SQL query.
- **tup_res**(`bool`) — inner parameter. Defaults to `False`. If using SQLite 3, can be set to `True` to get response as tuple instead of **mysqlite.Response**.

Returns **mysqlite.Response** containing result of a query, or a `tuple`, if mysqlite.DB.provider is `'sqlite3'` and `tup_res` is `True`.  
#### `raw_commit(query)`
This method can be used if `create_table()`, `insert()`, `update()` and `delete()` do not provide enough functionality.  
**Parameters**:
- **query**(`str`) — string containing completed SQL query.

Returns `True` on success, otherwise throws error of libraries-connections.

***

#### `class mysqlite.ResponseRow(db, table, value)`
Class, containing values of single record. Does not have standart methods.  
#### Property `mysqlite.ResponseRow.cols`
Returns list of column names that was requested in `mysqlite.DB.select()` or `mysqlite.DB.raw_select()`.  
#### Property `mysqlite.ResponseRow.values`
Returns list of values this row containing.  

Objects of this class have shortcut for `mysqlite.DB.update()`. So,
```python3
res = db.select('users', where = {'id': 1})[0]
db.update('users', balance = res.balance + 50, where = {'id': res.id})
res.balance += 50
```
is the same as
```python3
res = db.select('users', where = {'id': 1})[0]
res(balance = res.balance + 50)
```

***

#### `class mysqlite.Response(db, table, rows)`
Class, containing whole response of database on `SELECT` query.
Does not have methods, but have specific behaviour because of overloaded magic methods.
