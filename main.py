import ftplib
import sys
import os
import json
from generate_archive import GenerateArchive
from ftp_connect import FTPConnect


def upload_dir(session, directory):
    """
    Generate an archive thanks to the Generate Archive which creates a tar.gz file and deletes it after the process
    Send the archive to the FTP
    """
    with GenerateArchive(directory) as archive:
        with open(archive, 'rb') as file:
            filename = os.path.basename(file.name)
            session.storbinary(f'STOR {filename}', file)


def remove_old_files(session, directory, max_files):
    """
    Remove all the old files with start with the directory name
    """
    all_files = [x for x in session.nlst() if x.startswith(directory[directory.rindex('/') + 1:])]

    diff = len(all_files) - max_files
    if diff > 0:
        for file in all_files[:diff]:
            session.delete(file)


def upload_process(config_file):
    """
    First, get the config file and recover the the needed info
    Connect to the FTP thanks to the FTPConnect context manager which returns a session
    For each directory to be archived, the upload_dir function is invoked
    """
    with open(config_file) as config:
        json_config = json.load(config)
        directories = json_config['directories']
        ftp_host = json_config['ftp']['host']
        ftp_username = json_config['ftp']['username']
        ftp_password = json_config['ftp']['password']
        backup_dir = json_config.get('backup_dir', '')
        max_files = json_config.get('max_files', 5)

        with FTPConnect(host=ftp_host, username=ftp_username, password=ftp_password) as session:
            session.cwd(backup_dir)

            for directory in directories:
                upload_dir(session=session, directory=directory)
                remove_old_files(session=session, directory=directory, max_files=max_files)
                print(f'The directory "{directory}" uploaded to the FTP server!')


if __name__ == '__main__':
    # Get the config file argument
    try:
        config_file_argument = sys.argv[1:][0]
    except IndexError:
        sys.exit('Please add the configuration file name as argument.')

    # Get the config file absolute path
    config_file_path = os.path.abspath(config_file_argument.strip())

    # Open the config file
    try:
        upload_process(config_file_path)
    except FileNotFoundError:
        sys.exit(f'The file "{config_file_argument}" does not exist.')
    except ValueError:
        sys.exit('Not a json file.')
    except KeyError as e:
        sys.exit(f'The key {e} is needed in the config file.')
    except ftplib.all_errors as e:
        sys.exit(e)
