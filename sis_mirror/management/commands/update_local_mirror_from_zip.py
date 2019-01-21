import os
import re
import zipfile
import tempfile
import glob
from subprocess import call

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "My shiny new management command."
    DELIMITER = "\t"

    def add_arguments(self, parser):
        parser.add_argument('zipfile', nargs="?")

        parser.add_argument('--schema-file',
                            dest="schemafile",
                            nargs='?')

        parser.add_argument('--local-db',
                            dest="localdb",
                            nargs='?',
                            default='clarifycache')

        parser.add_argument('--clear-first',
                            action='store_true',
                            dest='clearfirst',
                            )
        
        parser.add_argument('--tables',
                            nargs="*")
        
        parser.add_argument('--exclude-tables',
                            nargs="*")

    def handle(self, *args, **options):
        zipfile_name = options["zipfile"]
        schemafile_name = options["schemafile"]
        localdb = options["localdb"]
        clearfirst = options["clearfirst"]
        tables=options["tables"]
        exclude_tables=options["exclude_tables"]

        if schemafile_name:
            self._update_schema(schemafile_name, localdb)

        if zipfile_name:
            self._update_mirror(zipfile_name, localdb, clearfirst=clearfirst,
                                tables=tables, exclude_tables=exclude_tables)

        self.stdout.write(self.style.SUCCESS(
            f"Completed update{' with schema' if schemafile_name else ''}."
        ))

    def _update_schema(self, schemafile_name, localdb):
        args = [
            'psql',
            '-d', localdb,
            '-f', schemafile_name
        ]

        return call(args)

    def _update_mirror(self, zipfile_name, localdb, clearfirst=False,
                       tables=None, exclude_tables=None):
        # Starting point for copying from a zip of dump files

        zip_ref = zipfile.ZipFile(zipfile_name, 'r')

        with tempfile.TemporaryDirectory() as tmpdirname:
            zip_ref.extractall(tmpdirname)

            # go through each file and process and update
            for filepath in glob.iglob(tmpdirname + '/clean_*.pgsql'):
                exit_code, table_name = self\
                    ._update_table_with_file(
                    filepath, localdb, clearfirst, tables, exclude_tables
                )
                
                if exit_code is not 0:
                    raise RuntimeError(f'Error updating {filepath}.')
                
                if table_name is not "SKIPPED":
                    print(f"\tTable {table_name} refreshed.")

    def _update_table_with_file(self, filepath, localdb, clearfirst=False,
                                tables=None, exclude_tables=None):
        # turn filename into sis table
        # EX: clean_2019-01-20--18-22_selectall_assignment_gsca_aff.pgsql
        filename = os.path.basename(filepath)
        table_name = self.filename_to_tablename(filename)
        if (exclude_tables and table_name in exclude_tables) or (
                tables and table_name not in tables):
            return 0, "SKIPPED"
        
        # clear the table if clearfirst
        if clearfirst:
            cleared = self._drop_all_from_table(table_name, localdb)
            if cleared is not 0:
                raise RuntimeError(f'Error deleting table "{table_name}".')
            print(f"\tDeleted all rows from {table_name}")

        # copy command with psql
        copy_command = \
            '\copy {} from \'{}\' csv delimiter \'{}\' null as \'NULL\'' \
                .format(table_name, filepath, self.DELIMITER)
        args = ['psql',
                '-d', localdb,
                '-c', copy_command
                ]

        return call(args), table_name

    @staticmethod
    def _drop_all_from_table(table_name, dbname):
        drop_command = f"delete from {table_name};"

        args = [
            'psql',
            '-d', dbname,
            '-c', drop_command
        ]

        return call(args)

    @staticmethod
    def filename_to_tablename(filename):
        regex = re.compile(
            r"^clean_\d{4}-\d{2}-\d{2}--\d{2}-\d{2}"
            r"_selectall_([\w_]+)\.pgsql$"
        )

        table_search = regex.search(filename)

        if table_search:
            return table_search.group(1)

        raise ValueError('No table name found in file.')

