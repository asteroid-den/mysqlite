import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, Union, List, Dict
import prettytable
import re
import json
import sqlite3
import itertools
from os import listdir, path

ALL = '*'
ASC = 'ASC'
DESC = 'DESC'

DB_NAME = ''
USER = 'root'
PASSWD = ''
HOST = ''
FILENAME = ''

GET_TABLES_SQLITE = 'SELECT name FROM sqlite_master WHERE type = "table";'
GET_COLUMNS_MYSQL = 'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = "%s" AND TABLE_NAME = "%s";'
GET_COLUMNS_SQLITE = 'SELECT name FROM PRAGMA_TABLE_INFO("%s");'


MySQLConn = pymysql.connections.Connection
SQLiteConn = sqlite3.Connection


def parse_where(where: Union[str, dict], provider: str) -> str:
    if type(where) is str:
        return where
    elif type(where) is dict:
        clauses = []
        for key in where.keys():
            clauses.append(f'{key} = %s' if provider == 'mysql' else f'{key} = ?')
        return ' AND '.join(clauses)


def parse_order(order: Union[str, list]) -> str:
    direction = ASC
    if type(order) is str:
        return order
    elif type(order) is list:
        if ASC in order:
            order.remove(ASC)
        elif DESC in order:
            order.remove(DESC)
            direction = DESC
    return ', '.join(order) + f' {direction}'


class DB:
    def __init__(self, db_name: str = None, user: str = None, passwd: str = None,
                 host: str = None, filename: str = None, table: str = None):

            # Only db_name + user (optional, default 'root') + passwd OR filename must be provided
            db_name = db_name or DB_NAME
            user = user or USER or 'root'
            passwd = passwd or PASSWD
            filename = filename or FILENAME
            host = host or HOST or 'localhost'

            if db_name and passwd:
                self.provider = 'mysql'
                self.db_name = db_name
                self.user = user
                self.passwd = passwd
                self.charset = 'utf8mb4'
                self.host = host

            elif filename:
                self.provider = 'sqlite3'
                self.filename = filename

            else:
                raise ValueError('Neither data for MySQL nor for SQLite provided')

            self.table = table

    def _create_conn(self) -> Union[MySQLConn, SQLiteConn]:
        if self.provider == 'mysql':
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.passwd,
                db=self.db_name,
                charset=self.charset,
                cursorclass=DictCursor
            )

        elif self.provider == 'sqlite3':
            conn = sqlite3.connect(self.filename)

        return conn

    @property
    def exists(self):
        if self.provider == 'sqlite3':
            return path.exists(self.filename)

        elif self.provider == 'mysql':
            try:
                conn = self._create_conn()
                conn.close()
                return True
            except pymysql.err.OperationalError:
                return False

    def push(push_type: str):
        def wrapper(func):
            def args_wrapper(self, *args, **kwargs):
                query, params = func(self, *args, **kwargs)
                conn = self._create_conn()

                if self.provider == 'mysql':
                    with conn.cursor() as cursor:
                        cursor.execute(query, params)

                elif self.provider == 'sqlite3':
                    cursor = conn.cursor()
                    cursor.execute(query, params)

                if push_type == 'commit':
                    conn.commit()
                    result = True

                elif push_type == 'fetch':
                    result = cursor.fetchall()
                    try:
                        table = re.search(r'FROM (?P<table>\w+)', query).group('table')
                    except AttributeError:
                        table = None

                    if self.provider == 'sqlite3':
                        if kwargs.get('tup_res', False):
                            return result
                        a_l = kwargs.get('args') or (args[1] if len(args) >= 2 else None) or ALL

                        if a_l == ALL:
                            cols = tuple(el[0] for el in self.raw_select(
                                GET_COLUMNS_SQLITE % table, tup_res=True))
                        else:
                            cols = [a_l] if type(a_l) is str else (
                                a_l if type(a_l) is list else
                                list(a_l.values()))

                        result = list(dict(zip(cols, row)) for row in result)
                    result = Response(self, table, result)
                else:
                    raise ValueError('Push type can be equal to "commit" or "fetch" only')
                conn.close()
                return result
            return args_wrapper
        return wrapper

    @push('commit')
    def insert(self, table: str = None, dic: dict = None, **kwargs):
        statement = 'INSERT INTO {table} ({keys}) VALUES ({values});'
        table = table or self.table
        dic = dic or kwargs
        vals = []

        for value in dic.values():
            vals.append(value)

        statement = statement.format(
            keys=', '.join(dic.keys()),
            values=', '.join((['%s'] if self.provider == 'mysql' else ['?']) * len(vals)),
            table=table)

        return statement, tuple(vals)

    @push('fetch')
    def select(self, table: str = None, args: Union[list, str, dict] = ALL,
               where: Union[str, dict] = None, group_by: str = None,
               order_by: Union[list, str] = None, limit: int = None):

            statement = 'SELECT {values} FROM {table}'
            table = table or self.table

            if where:
                statement += f' WHERE {parse_where(where, self.provider)}'

            if group_by:
                statement += f' GROUP BY {group_by}'

            if order_by:
                statement += f' ORDER BY {parse_order(order_by)}'

            if limit:
                statement += f' LIMIT {limit}'

            statement += ';'

            if type(args) is dict:
                statement = statement.format(
                    values=', '.join([f'{column} AS {column_key}'
                                     for column, column_key in
                                     args.items()]),
                    table=table)
            else:
                args = args if type(args) is list else [args]
                statement = statement.format(
                    values=', '.join(args),
                    table=table)

            where_vals = tuple(
                where.values()) if type(where) is dict else tuple()
            return statement, where_vals

    @push('commit')
    def update(self, table: str = None, dic: dict = None, where: Union[str, dict] = None, **kwargs):
            statement = 'UPDATE {table} SET {pairs}'
            table = table or self.table
            dic = dic or kwargs

            if where:
                statement += f' WHERE {parse_where(where, self.provider)}'
            statement += ';'
            keys, vals = [], []

            for key, value in dic.items():
                keys.append(f'{key} = %s' if self.provider == 'mysql' else f'{key} = ?')
                vals.append(value)

            statement = statement.format(pairs=', '.join(keys), table=table)
            where_vals = tuple(where.values()) if type(where) is dict else tuple()
            return statement, tuple(vals) + where_vals

    @push('commit')
    def delete(self, table: str, where: Union[str, dict] = None):
        table = table or self.table
        statement = f'DELETE FROM {table}'

        if where:
            statement += f' WHERE {parse_where(where, self.provider)}'

        statement += ';'
        where_vals = tuple(where.values()) if type(where) is dict else tuple()
        return statement, where_vals

    @push('commit')
    def create_table(self, name: str, fields: Union[Dict[str, str], str]):

        if type(fields) is dict:
            t_fields = '(' + ', '.join(
                [f'{key} {value}' for key, value in fields.items()]) + ')'

        elif type(fields) is str:
            borders = fields[0], fields[-1]

            if ''.join(borders) != '()':
                t_fields = f'({fields})'

        return f'CREATE TABLE {name} {t_fields};', tuple()

    @push('fetch')
    def raw_select(self, query: str, params: tuple = (), tup_res: bool = False):
        return query, params

    @push('commit')
    def raw_commit(self, query: str, params: tuple = ()):
        return query, params


class ResponseRow:

    def __init__(self, db: DB, table: str, values: dict):
        self._db = db
        self._vals = values
        self.table = table

        for key, value in values.items():
            if type(value) is str and value.startswith('!JSON'):
                value = json.loads(value.lstrip('!JSON'))

            setattr(self, key, value)

    @property
    def cols(self):
        return self._vals.keys()

    @property
    def values(self):
        return self._vals.values()

    def __call__(self, **kwargs):
        self._db.update(self.table, kwargs, where=self._vals)
        for name, value in kwargs.items():
            self.__setattr__(name, value)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return json.dumps(self._vals, indent=4, ensure_ascii=False)


class Response:

    def __init__(self, db: DB, table: Optional[str] = None, rows: List[dict] = []):
        self.rows = []
        self.type = table or db.table

        if len(rows) == 1:
            for key, value in rows[0].items():
                if type(value) is str and value.startswith('!JSON'):
                    value = json.loads(value.lstrip('!JSON'))
                setattr(self, key, value)

        elif len(rows) == 0:
            if db.provider == 'mysql':
                get_columns = GET_COLUMNS_MYSQL % (db.db_name, table)

            elif db.provider == 'sqlite3':
                get_columns = GET_COLUMNS_SQLITE % table

            for row in db.raw_select(get_columns):

                if db.provider == 'mysql':
                    setattr(self, row.COLUMN_NAME, None)

                elif db.provider == 'sqlite3':
                    setattr(self, row.cid, None)

        for row in rows:
            self.rows.append(ResponseRow(db, table, row))

    def __iter__(self):
        for row in self.rows:
            yield row

    def __next__(self):
        return next(self.__iter__())

    def __str__(self):
        table = prettytable.PrettyTable()
        table.hrules = prettytable.ALL

        if self.rows:
            table.field_names = self.rows[0].cols
            for record in self.rows:
                table.add_row(record.values)

        return table.get_string()

    def __getitem__(self, key: Union[str, int]):
        if type(key) is int:
            return self.rows[key]
        else:
            return [getattr(i, key) for i in self.rows]

    def __bool__(self):
        return bool(len(self))

    def __len__(self):
        return len(self.rows)

__all__ = ['ALL', 'ASC', 'DESC', 'parse_where', 'parse_order', 'DB']

__version__ = '0.0.4'
