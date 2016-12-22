#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import migrant
import os.path
import sqlite3
import subprocess
import tempfile
import unittest


TEST_DATABASE_DIR = os.path.abspath('test_databases')
TEST_DATABASES = {
    0: os.path.join(TEST_DATABASE_DIR, '001_after_add_table_post.dump.sql'),
    1: os.path.join(TEST_DATABASE_DIR, '002_after_add_table_author.dump.sql'),
    2: os.path.join(TEST_DATABASE_DIR, '003_after_add_table_text.dump.sql')
}
TEST_MIGRATION_DIR = os.path.abspath('test_migrations')
TEST_MIGRATIONS = {
    0: os.path.join(TEST_MIGRATION_DIR, '000_FULL.sql'),
    1: os.path.join(TEST_MIGRATION_DIR, '001_add_table_author.sql'),
    2: os.path.join(TEST_MIGRATION_DIR, '002_add_table_text.sql')
}


def _sqlite3_dump(filename):
    """Catch the 'dump' via shell binary, 'conn.iterdump()' always generates different output,

    :param filename: SQLite database file name
    :return: Database dump as str
    """
    return str(subprocess.check_output(['sqlite3', filename, '.dump']), 'utf-8').split('\n')


class TestMigrant(unittest.TestCase):
    def test_list_migrations(self):
        expected_migrations = TEST_MIGRATIONS
        migrations = migrant.list_migrations(TEST_MIGRATION_DIR)
        self.assertDictEqual(migrations, expected_migrations)

    def test_get_schema_version(self):
        expected_schema_version = 0
        with tempfile.NamedTemporaryFile() as db_file:
            with sqlite3.connect(db_file.name) as conn:
                cur_ver = migrant.get_schema_version(conn)
                self.assertEqual(cur_ver, expected_schema_version)

    def test_set_schema_version(self):
        expected_schema_version = 1
        with tempfile.NamedTemporaryFile() as db_file:
            with sqlite3.connect(db_file.name) as conn:
                migrant.set_schema_version(conn, expected_schema_version)
                cur_ver = migrant.get_schema_version(conn)
                self.assertEqual(cur_ver, expected_schema_version)

    def test_get_target_schema_version(self):
        expected_target_version = 2
        target_version = migrant.get_target_schema_version(TEST_MIGRATIONS)
        self.assertEqual(target_version, expected_target_version)

    def test_run_migration_initial(self):
        """Applies TEST_MIGRATIONS[0] from scratch.

        Result should match TEST_DATABASES[0]. Runs no 'real' migrations but
        rather creates the full DB at once.
        """
        with tempfile.NamedTemporaryFile() as db_file:
            with sqlite3.connect(db_file.name) as conn:
                # Arrange, act
                migrant.run_migration(conn, TEST_MIGRATIONS[0])
            db_file_dump = _sqlite3_dump(db_file.name)
        # Assert
        self._compare_dumps(TEST_MIGRATIONS[0], db_file_dump)

    def test_run_migration_first_to_second(self):
        """Applies TEST_MIGRATIONS[1] on TEST_DATABASES[0].

        Result should match TEST_DATABASES[1].
        """
        self._apply_run_migration(TEST_MIGRATIONS[1], TEST_DATABASES[0], TEST_DATABASES[1])

    def test_run_migration_second_to_third(self):
        """Applies TEST_MIGRATIONS[2] on TEST_DATABASES[1].

        Result should match TEST_DATABASES[2].
        """
        self._apply_run_migration(TEST_MIGRATIONS[2], TEST_DATABASES[1], TEST_DATABASES[2])

    @unittest.skip("")
    def test_migrate_initial(self):
        pass

    @unittest.skip("")
    def test_migrate_initial_to_first(self):
        pass

    @unittest.skip("")
    def test_migrate_first_to_second(self):
        pass

    def _apply_run_migration(self, migration, initial_database, expected_database):
        """ Utility method to apply a migration to an initial database and compare with an expected one.

        :param migration: The migration to apply
        :param initial_database: The database to apply on
        :param expected_database: The expected database after applying
        """
        with tempfile.NamedTemporaryFile() as db_file:
            with sqlite3.connect(db_file.name) as conn:
                # Arrange
                with open(initial_database) as prepared:
                    conn.executescript(prepared.read())
                # Act
                migrant.run_migration(conn, migration)
            db_file_dump = _sqlite3_dump(db_file.name)
        # Assert
        self._compare_dumps(expected_database, db_file_dump)

    def _compare_dumps(self, expected, current):
        """Compares two SQLite dumps for equality.

        :param expected: First dump
        :param current: Second dump
        :return: True, if they are equal, False otherwise
        """
        with open(expected) as expected_dump_file:
            for current_dump, expected_dump in zip(current, expected_dump_file):
                self.assertEqual(current_dump + '\n', expected_dump)


if __name__ == '__main__':
    unittest.main()
