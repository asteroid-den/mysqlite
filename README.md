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

### class mysqlite.DB(*db_name=None, user='root', passwd=None, filename=None, table=None*)
Main class to interact with DBs. Only `db_name` + `passwd` + `user` (user is optional) for connecting to MySQL DB **or** `filename` for connectiong to SQLite3 DB must be provided. You can specify a `table` if you want not to specify it in every request.
#### create_table(*name, fields*)
**Parameters**
- **name**(`str`) — a name of new table
- **fields**(`dict`|`str`) — description of columns. Must be provided as dictionary, where keys are column names and values are characteristics of this column, or as a total description of all columns in a single string **without opening and closing parantheses**.  
#### insert(*table, dic, \*\*kwargs*)
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
#### select(*table, args\_list, where, order\_by, group\_by, limit*)
**Parameters**
- **table**(`str`, _optional_) — name of table to retrieve values. Can be omitted, if table was specified when created `mysqlite.DB` instance.
- **args_list**(`list`|`str`, _optional_) — column names from which values will be retrived. Can be `str`, if only 1 column needed, or `list`, if few columns needed. Defaults to **mysqlite.ALL**. Can be ommited if you want to use default value or if you 
- **where**(`str`|`dict`, _optional_) — condition, that filters values from table. Can be provided as dictionary, where keys are column names and values are conditions, or as a total condition in a single string.
- **order_by**(`str`, _optional_) — sorting of a result ascending or descending. Can be `'ASC'` or `'DESC'`, which can also be provided as **mysqlite.ASC** and **mysqlite.DESC**.
- **group_by**(`str`, _optional_) — used to group result by specific column.
- **limit**(`int`, _optional_) — used to limit the amount of records that goes to result.
Returns **mysqlite.Response** object containing result of query.  
#### update(*table, dic, where, \*\*kwargs*)
**Parameters**
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
#### delete(*table, where*)
**Parameters**
- **table**(`str`, _optional_) — name of table to delete values. Can be omitted, if table was specified when created `mysqlite.DB` instance.
- **where**(`str`|`dict`, _optional_) — condition, that filters values from table. Can be provided as dictionary, where keys are column names and values are conditions, or as a total condition in a single string.
**_Do not_** use **delete()** method without specifying this parameter in most cases, because in this case you'll delete **_ALL_** records. Results of processing SQL queries are irreversible, so you can lose some data.  

***


