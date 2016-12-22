#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple SQLite database migrations.

Expects plain SQL files...
"""
import argparse
import fnmatch
import os
import sqlite3
import sys


def list_migrations(folder):
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


def get_schema_version(cursor):
    """Retrieves the database schema version.

    Essentially executes "PRAGMA user_version;" and returns the result.

    :param cursor: SQLite database cursor
    :return: Current schema version
    """
    return cursor.execute('PRAGMA user_version;').fetchone()[0]


def set_schema_version(cursor, version):
    """Update the the database schema version.

    :param cursor: SQLite database cursor
    :param version: New schema version
    """
    # This doesn't work: cursor.execute('PRAGMA user_version = ?;', (int(version),))
    cursor.execute("PRAGMA user_version = '{v:d}';".format(v=version))


def get_target_schema_version(migrations):
    """Returns the target schema version.

    Should match the number of the latest migration available.

    :param migrations: Migrations dictionary
    :return: Desired schema version
    """
    return len(migrations.keys()) - 1


def run_migration(cursor, migration_filename):
    """Executes a migration.

    :param cursor: SQLite database cursor
    :param migration_filename: File containing SQL statements to execute
    """
    with open(migration_filename) as migration_file:
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
    migrations = list_migrations(migrations_folder)

    with sqlite3.connect(database_file) as conn:
        current_version = get_schema_version(conn)
        target_version = get_target_schema_version(migrations)
        if current_version == 0:
            run_migration(conn, migrations[0])
            set_schema_version(conn, target_version)
        else:
            while current_version < target_version:
                next_version = current_version + 1
                run_migration(conn, migrations[next_version])
                set_schema_version(conn, next_version)
                current_version = next_version


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='migrant', description='SQLite migration engine')
    subparsers = parser.add_subparsers(title='sub-commands', help='sub-command help')
    migrate_parser = subparsers.add_parser('migrate', help='run migrations')
    migrate_parser.add_argument('db', type=str, help="SQLite database file")
    migrate_parser.add_argument('-m', '--migrations-folder', type=str,
                                help='folder containing SQLite migration files')
    #start_migration_parser = subparsers.add_parser('start-migration', help='create a new migration')

    args = parser.parse_args(sys.argv)
