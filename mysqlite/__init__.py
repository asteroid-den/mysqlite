import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, Union, List, Dict
from prettytable import PrettyTable
import re
import json
import sqlite3
import itertools

ALL = '*'
ASC = 'ASC'
DESC = 'DESC'

GET_TABLES_SQLITE = 'SELECT name FROM sqlite_master WHERE type = "table";'
GET_COLUMNS_MYSQL = 'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = "%s" AND TABLE_NAME = "%s";'
GET_COLUMNS_SQLITE = 'SELECT name FROM PRAGMA_TABLE_INFO("%s");'


MySQLConn = pymysql.connections.Connection
SQLiteConn = sqlite3.Connection


def parse_where(where: Union[str, dict]) -> str:
        if type(where) is str:
            return where
        elif type(where) is dict:
            clauses = []
            for key, value in where.items():
                if type(value) is str:
                    clauses.append(f'{key} = "{value}"')
                else:
                    clauses.append(f'{key} = {value}')
            return ' AND '.join(clauses)


class DB:

    def __init__(
                self, db_name: str=None, user: str='root', passwd: str=None,
                filename: str=None, table: str=None):
            # Only db_name + user (optional, default 'root') + passwd OR filename must be provided
            if db_name and passwd:
                self.provider = 'mysql'
                self.db_name = db_name
                self.user = user
                self.passwd = passwd
                charset = 'utf8mb4'
                host = 'localhost'
            elif filename:
                if re.match(r'^[\w,\s-]+\.db$', filename):
                    self.provider = 'sqlite3'
                    self.filename = filename
                else:
                    raise ValueError('Invalid filename provided')
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

    def push(push_type: str):
        def wrapper(func):
            def args_wrapper(self, *args, **kwargs):
                query = func(self, *args, **kwargs)
                conn = self._create_conn()
                if self.provider == 'mysql':
                    with conn.cursor() as cursor:
                        cursor.execute(query)
                elif self.provider == 'sqlite3':
                    cursor = conn.cursor()
                    cursor.execute(query)
                if push_type == 'commit':
                    conn.commit()
                    result = True
                elif push_type == 'fetch':
                    result = cursor.fetchall()
                    table = re.search(r'FROM (?P<table>\w+)',
                                      query).group('table')
                    if self.provider == 'sqlite3':
                        if kwargs.get('tup_res', False):
                            return result
                        cols = tuple(el[0] for el in self.raw_select(
                            GET_COLUMNS_SQLITE % table, tup_res=True))
                        result = list(dict(zip(cols, row)) for row in result)
                    result = Response(self, table, result)
                else:
                    raise ValueError('Push type can be equal to "commit" or "fetch" only')
                conn.close()
                return result
            return args_wrapper
        return wrapper

    @push('commit')
    def insert(self, table: str=None, dic: dict=None, **kwargs):
        statement = 'INSERT INTO {table} ({keys}) VALUES ({values});'
        table = self.table if not table
        dic = kwargs if not dic
        vals = []
        for value in dic.values():
            if type(value) is str:
                value = value.replace('"', '\\"')
                vals.append(f'"{value}"')
            elif value is None:
                vals.append('NULL')
            else:
                vals.append(str(value))
        statement = statement.format(
            keys=', '.join(dic.keys()),
            values=', '.join(vals),
            table=table)

        return statement

    @push('fetch')
    def select(self, table: str=None, args_list: Union[list, str]=ALL,
            where: Union[str, dict]=None, order_by: str=None,
            sort_by: str=None, limit: int=None, *args):

            statement = 'SELECT {values} FROM {table}'
            table = self.table if not table
            if where:
                statement += f' WHERE {parse_where(where)}'
            if order_by:
                if order_by in [ASC, DESC]:
                    statement += f' ORDER BY {order_by}'
                else:
                    raise ValueError('order_by can be "ASC" and "DESC" only')
            if group_by:
                statement += f' GROUP BY {group_by}'
            if sort_by:
                statement += f' SORT BY {sort_by}'
            if limit:
                statement += f' LIMIT {limit}'
            statement += ';'
            args_list = args if not args_list
            if type(args_list) is not list:
                args_list = [args_list]
            statement = statement.format(
                values=', '.join(args_list),
                table=table)

            return statement

    @push('commit')
    def update(self, table: str=None, dic: dict=None,
               where: Union[str, dict]=None, **kwargs):

            statement = 'UPDATE {table} SET {pairs}'
            table = self.table if not table
            dic = kwargs if not dic
            if where:
                statement += f' WHERE {parse_where(where)}'
            statement += ';'
            vals = []
            for key, value in dic.items():
                if type(value) is str:
                    vals.append(f'{key} = "{value}"')
                elif value is None:
                    vals.append(f'{key} = NULL')
                else:
                    vals.append(f'{key} = {value}')
            statement = statement.format(
                pairs=', '.join(vals),
                table=table)

            return statement

    @push('commit')
    def delete(self, table: str, where: Union[str, dict]=None):
        table = self.table if not table
        statement = f'DELETE FROM {table}'
        if where:
            statement += f' WHERE {parse_where(where)}'
        statement += ';'
        return statement

    @push('commit')
    def create_table(self, name: str, fields: Union[Dict[str, str], str]):
        if type(fields) is dict:
            t_fields = '(' + ', '.join(
                [f'{key} {value}' for key, value in fields.items()]) + ')'
        elif type(fields) is str:
            t_fields = f'({fields})'
        return f'CREATE TABLE {name} {t_fields};'

    @push('fetch')
    def raw_select(self, query: str, tup_res: bool = False):
        return query

    @push('commit')
    def raw_commit(self, query: str):
        return query


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

    def __call__(self, name, value):
        self._db.update(self.table, {name: value},
                        where=parse_where(self._vals))
        self.__setattr__(name, value)


class Response:
    def __init__(self, db: DB, table: str, rows: Optional[List[dict]] = []):
        self.rows = []
        self.type = table
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
        table = PrettyTable()
        if self.rows:
            table.field_names = self.rows[0].cols
            for record in self.rows:
                table.add_row(record.values)

        return table.get_string()

    def __getitem__(self, key: Union[str, int]):
        if key.isdigit():
            return self.rows[key]
        else:
            return [getattr(i, key) for i in self.rows]

    def __bool__(self):
        return bool(len(self.rows))

__all__ = ['ALL', 'ASC', 'DESC', 'parse_where', 'DB']
