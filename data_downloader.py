import argparse
import os
import paramiko
import sys
from tqdm import tqdm

def download_dir(sftp, remote_dir, local_dir):
    """
    Recursively download files from a remote SFTP directory to a local directory with progress bar.
    Args:
    - sftp: An active SFTP session
    - remote_dir: The remote directory path
    - local_dir: The local directory path where files will be downloaded
    """
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    sftp.chdir(remote_dir)
    file_list = sftp.listdir_attr()

    for file_attr in file_list:
        remote_file = os.path.join(remote_dir, file_attr.filename)
        local_file = os.path.join(local_dir, file_attr.filename)

        if file_attr.longname.startswith('d'):  # If it's a directory
            download_dir(sftp, remote_file, local_file)
        else:  # If it's a file
            if not os.path.exists(local_file):  # Check if the file exists locally
                with tqdm(total=file_attr.st_size, unit='B', unit_scale=True, unit_divisor=1024) as progress_bar:
                    sftp.get(remote_file, local_file, callback=lambda x, y: progress_bar.update(y))
                print(f"Downloaded {remote_file} to {local_file}")
            else:
                print(f"Skipped {remote_file} as it already exists locally")

def count_remote_files(sftp, remote_dir):
    """
    Count the total number of files in a remote SFTP directory.
    Args:
    - sftp: An active SFTP session
    - remote_dir: The remote directory path
    Returns:
    - total_files: Total number of files in the remote directory
    """
    sftp.chdir(remote_dir)
    file_list = sftp.listdir()
    total_files = len(file_list)
    return total_files

def setup_sftp_connection(url, username, password):
    """
    Set up and return an SFTP connection.
    Args:
    - url: URL of the SFTP server
    - username: SFTP username
    - password: SFTP password
    """
    try:
        transport = paramiko.Transport((url, 22))
        transport.connect(username=username, password=password)
        return paramiko.SFTPClient.from_transport(transport)
    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials.")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"SSH connection error: {e}")
        sys.exit(1)

def main(args):
    remote_dir = args.remote_dir
    local_dir = os.path.join(os.path.expanduser(args.local_dir), os.path.basename(remote_dir))

    sftp = setup_sftp_connection(args.url, args.username, args.password)

    try:
        total_remote_files = count_remote_files(sftp, remote_dir)
        download_dir(sftp, remote_dir, local_dir)
        local_files = os.listdir(local_dir)
        total_local_files = len(local_files)

        print(f"Total remote files: {total_remote_files}")
        print(f"Total local files: {total_local_files}")

    finally:
        sftp.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download files from SFTP server.')
    parser.add_argument('--url', required=True, help='URL of the SFTP server')
    parser.add_argument('--username', required=True, help='SFTP username')
    parser.add_argument('--password', required=True, help='SFTP password')
    parser.add_argument('--remote-dir', required=True, help='Remote directory to download from')
    parser.add_argument('--local-dir', required=True, help='Local directory to download to')

    args = parser.parse_args()
    main(args)
