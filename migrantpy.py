#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2016 Sascha Peilicke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import fnmatch
import os
import sqlite3
import re

__doc__ = 'Simple SQLite database migrations'
__docformat__ = 'restructuredtext en'
__author__ = 'Sascha Peilicke <sascha@peilicke.de>'
__version__ = '1.0.0'


def _list_migrations(folder):
    """Returns a dict of migration files.

    Valid migration files have to match the glob '*_*.sql'.

    :param folder: The folder containing migration files
    :return: Dictionary mapping version numbers to migrations
    """
    migrations = {}
    for basename in os.listdir(folder):
        if fnmatch.fnmatch(basename, '*_*.sql'):
            number = int(basename.split('_', 1)[0])
            migrations[number] = os.path.join(folder, basename)
    return migrations


def _get_schema_version(cursor):
    """Retrieves the database schema version.

    Essentially executes "PRAGMA user_version;" and returns the result.

    :param cursor: SQLite database cursor
    :return: Current schema version
    """
    return cursor.execute('PRAGMA user_version;').fetchone()[0]


def _set_schema_version(cursor, version):
    """Update the the database schema version.

    :param cursor: SQLite database cursor
    :param version: New schema version
    """
    # This doesn't work: cursor.execute('PRAGMA user_version = ?;', (int(version),))
    cursor.execute("PRAGMA user_version = '{v:d}';".format(v=version))


def _get_target_schema_version(migrations):
    """Returns the target schema version.

    Should match the number of the latest migration available.

    :param migrations: Migrations dictionary
    :return: Desired schema version
    """
    mkeys = list(migrations.keys())
    mkeys.sort(reverse=True)
    return mkeys[0]


def _run_migration(cursor, migration_filename):
    """Executes a migration.

    :param cursor: SQLite database cursor
    :param migration_filename: File containing SQL statements to execute
    """
    if migration_filename is None:
        return None

    with open(migration_filename) as migration_file:
        print(f"Migrating {migration_filename} ...")
        migration_sql = migration_file.read()
        cursor.executescript(migration_sql)


def migrate(database_file, migrations_folder):
    """Migrate database to latest state.

    Either runs all not previously run migrations against an existing
    database or creates a new one with equivalent content.

    :param database_file:
    :param migrations_folder:
    :return:
    """
    migrations = _list_migrations(migrations_folder)

    with sqlite3.connect(database_file) as conn:
        current_version = _get_schema_version(conn)
        target_version = _get_target_schema_version(migrations)
        next_version = current_version + 1
        while next_version <= target_version:
            _run_migration(conn, migrations.get(next_version))
            _set_schema_version(conn, next_version)
            next_version += 1


def _create_migration(name, migrations_folder):
    migrations = os.listdir(migrations_folder)
    migrations.sort()
    try:
        current_version = int( re.match(r"^(\d+)", migrations[-1]).group(1))
    except Exception as err:
        current_version = 0
    next_version_str = str(current_version+1).zfill(3)
    migration_name = f"{next_version_str}_{re.sub(r'[^0-9A-Za-z_]', '_', name)}.sql"
    migration_path = os.path.join(migrations_folder, migration_name)
    print(f'Creating {migration_path} ...')
    open(migration_path, 'a').close()


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(__version__))
    subparsers = parser.add_subparsers()

    parser_migrate = subparsers.add_parser('migrate', help='run migrations on a SQLite database file')
    parser_migrate.add_argument('database', help="SQLite database file")
    parser_migrate.add_argument('migrations', help="database migrations folder")
    parser_migrate.set_defaults(func=lambda args: migrate(args.database, args.migrations))

    parser_create_migration = subparsers.add_parser('create', help='create a new migration')
    parser_create_migration.add_argument('name', help='migration name, e.g. \'my new migration\'')
    parser_create_migration.add_argument('--migrations', help="database migrations folder, or default 'migrations'", default='./migrations', required=False)
    parser_create_migration.set_defaults(func=lambda args: _create_migration(args.name, args.migrations))

    parser_help = subparsers.add_parser('help', help='show this help')
    parser_help.set_defaults(func=lambda args: parser.print_help())

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        # Show help if no arguments are passed
        args = argparse.Namespace(func=parser_help.get_default('func'))

    args.func(args)  # Invoke default funcs


if __name__ == '__main__':
    _main()
