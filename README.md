## MySQLite

**Minimalistic MySQL and SQLite 3 ORM**  

### Examples

> Python console, working with SQLite 3
```pycon
>>> from mysqlite import *
>>> db = DB(filename = 'test.db')
>>> db.create_table('users', {'id': 'INT NOT NULL', 'balance': 'FLOAT NOT NULL DEFAULT 50'})
>>> db.insert('users', {'id': 1})
>>> db.insert('users', {'id': 2, 'balance': 100})
>>> print(db.select('users'))
+----+---------+
| id | balance |
+----+---------+
| 1  |    50   |
| 2  |   100   |
+----+---------+
```

> Python 3 file
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
