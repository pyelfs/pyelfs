# Pyelfs

Python packaged tools to manage git-lfs objects without any http server.
The feature of git-lfs [custom transfer agent](https://github.com/git-lfs/git-lfs/blob/master/docs/custom-transfers.md) is used.

Implemented commands
- file_agent
    - transfer lfs-objects to a local directory directly.
- sftp_agent
    - transfer lfs-objects to a directory in a sftp server.

## Recommends

- [git-lfs/2.11.0 or newer](https://github.com/git-lfs/git-lfs)
    - 'git lfs install' should be executed.
## Install

```bash
pip install git+https://github.com/kyusque/pyelfs
```

## Setup in a git directory (first only)

### Mac OS or Unix system

#### File agent

```bash
git lfs install
git config --add lfs.customtransfer.pyelfs.path file_agent.py
git config --add lfs.customtransfer.pyelfs.args '--lfs-dir /home/{username}/{dirname}'
git config --add lfs.standalonetransferagent pyelfs
```

#### SFTP agent

```bash
git lfs install
git config --add lfs.customtransfer.pyelfs.path sftp_agent.py
git config --add lfs.customtransfer.pyelfs.args '--hostname {hostname} --user {username} --rsa-key {rsa key path} --remote-dir pyelfs:///home/{username}/{dirname}'
git config --add lfs.standalonetransferagent pyelfs
```
- Add 'pyelfs://' to the remote path (e.g. pyelfs:///home/user/lfs-objects) in order to avoid unintentional path expansion by git-lfs.

### Windows OS

#### File agent

```bash
git lfs install
git config --add lfs.customtransfer.pyelfs.path file_agent.exe
git config --add lfs.customtransfer.pyelfs.args '--lfs-dir /home/{username}/{dirname}'
git config --add lfs.standalonetransferagent pyelfs
```

#### SFTP agent

```bash
git lfs install
git config --add lfs.customtransfer.pyelfs.path sftp_agent.exe
git config --add lfs.customtransfer.pyelfs.args '--hostname {hostname} --user {username} --rsa-key {rsa key path} --remote-dir pyelfs:///home/{username}/{dirname}'
git config --add lfs.standalonetransferagent pyelfs
```
- Add 'pyelfs://' to the remote path (e.g. pyelfs:///home/user/lfs-objects) in order to avoid unintentional path expansion by git-lfs.

## Examples

### git push

```bash
git lfs track "*.jpg"
wget https://upload.wikimedia.org/wikipedia/commons/6/66/Tofu_4.jpg
git add .gitattributes Tofu_4.jpg
git commit -m "track jpg"
```

```bash
git remote add origin {your remote git repository}
git push -u orgin master
```

### git clone or pull

```bash
git fetch origin {your remote git repository}
git reset --hard origin/master
```

## Tips

- Temporary directory
    - Addition of `--temp-dir {dir path}` into `lfs.customtransfer.pyelfs.args` sets temporary directory.
    - In download stage, temporary files should be downloaded to the same partition as the git directory.
- Debug log
    - Addition of `--debug-log {log file}` into `lfs.customtransfer.pyelfs.args` outputs a debug log.
    - If you set this and you still don't see any log output, check .git/config setting or git-lfs version.
- With GitHub repository
    - If the first git lfs config for `standalonetransferagent` fails, it will use GitHub's LFS hosting service (default).
    - In that case, even if you fix it later, you will not be able to push lfs objects with GH008 error 
        - You'll have to delete the repository and rebuild it.
    - So be careful in the very first push with lfs objects
        - After this, you can avoid the mistake because 'git clone' will not be correctly executed. 


## Reference

- https://github.com/git-lfs/git-lfs/blob/master/docs/custom-transfers.md