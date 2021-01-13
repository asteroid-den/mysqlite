## MySQLite

**Minimalistic MySQL and SQLite 3 ORM**  

### Examples
```python3
>>> from mysqlite import *
>>> db = DB(filename = 'test.db')
>>> db.create_table('users', {'id': 'INT NOT NULL', 'balance': 'FLOAT NOT NULL DEFAULT 50'})
>>> db.insert('users', {'id': 1})
>>> db.insert('users', {'id': 2, 'balance': 100})
>>> print(db.select('users')
+----+---------+
| id | balance |
+----+---------+
| 1  |    50   |
| 2  |   100   |
+----+---------+
```
