# PyElfs

Git LFS transfer agent to manage git-lfs objects without any http server.
The feature of git-lfs [custom transfer](https://github.com/git-lfs/git-lfs/blob/master/docs/custom-transfers.md) is used.

Implemented commands
- pyelfs file
    - Transfer lfs-objects to a local directory directly.
- pyelfs sftp
    - transfer lfs-objects to a directory in a sftp server.
- pyelfs null
    - do nothing. 

## Recommends

- [git-lfs/2.11.0 or newer](https://github.com/git-lfs/git-lfs)
    - 'git lfs install' should be executed.
## Install

```bash
pip install git+https://github.com/pyelfs/pyelfs
```

## Setup in a git repository

Hit `pyelfs init {agent name}` and exec output commands in your git repository.

 
```bash
[init command]
pyelfs init file

[output]
### PyElfs
### Please execute the following commands in your git repository.
### pyelfs init file -h shows more info.

git config --add lfs.standalonetransferagent pyelfs
git config --add lfs.customtransfer.pyelfs.path pyelfs
git config --add lfs.customtransfer.pyelfs.args 'file --lfs-storage-local pyelfs://~/.lfs-miscellaneous'

```

## Examples

### Push

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

### Fetch

```bash
git fetch origin {your remote git repository}
git reset --hard origin/master
```

## Tips

- Temporary directory
    - Addition of `--temp {dir path}` into `lfs.customtransfer.pyelfs.args` sets temporary directory.
    - In download stage, temporary files should be downloaded to the same partition as the git directory.
- Debug log
    - Addition of `--verbose {log file}` into `lfs.customtransfer.pyelfs.args` outputs a debug log.
    - If you set this and you still don't see any log output, check .git/config setting or git-lfs version.
- With GitHub repository
    - If the first git lfs config for `standalonetransferagent` fails, it will use GitHub's LFS hosting service (default).
    - In that case, even if you fix it later, you will not be able to push lfs objects with GH008 error 
        - You'll have to delete the repository and rebuild it.
    - So be careful in the very first push with lfs objects
        - After this, you can avoid the mistake because 'git clone' will not be correctly executed. 


## Reference

- https://github.com/git-lfs/git-lfs/blob/master/docs/custom-transfers.md