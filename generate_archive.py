import os
import sys
import tarfile
import time


class GenerateArchive:
    """
    A context manager which create and return an archive
    And delete it on exit
    """
    def __init__(self, directory):
        self.directory = directory

    def __enter__(self):
        archive = self._create_archive()
        return archive

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._delete_archive()

    def _create_archive(self):
        directory_absolute_path = os.path.abspath(self.directory)
        archive_time = time.strftime('_%Y_%m_%d_%H%M%S')
        output = f'{directory_absolute_path}{archive_time}.tar.gz'

        with tarfile.open(output, "w:gz") as tar:
            try:
                tar.add(self.directory)
            except FileNotFoundError:
                os.remove(tar.name)
                sys.exit(f'The directory "{self.directory}" does not exist.')

            self.output = tar.name

        return self.output

    def _delete_archive(self):
        os.remove(self.output)
