# sftp-toolkit

The repository hosts a collection of scripts designed for streamlined and automated interactions with SFTP servers.

### Data downloader

This Python script automates the process of recursively downloading files and directories from a specified SFTP server location to a local directory.

```
conda env sftp-toolkit

conda activate sftp-toolkit

python data_downloader.py --url sftp.example.com --username my_username --password my_password --remote-dir /path/to/remote/directory --local-dir /path/to/local/directory
```