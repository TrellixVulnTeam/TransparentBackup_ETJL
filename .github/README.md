# Transparent Backup

Transparent Backup is an incremental backup tool that is focused on making snapshots that are free-standingly accessible (by storing them as partial mirrors of the source directory tree) and free-standingly restorable (by supplying Python, Bash or cmd scripts to do the leg-work), while still de-duplicating at the file level and avoiding needing access to previous snapshots' contents (relying instead on a file describing the directory tree and the contents' metadata).

## Licence

The content of the TransparentBackup repository is free software; you can redistribute it and/or modify it under the terms of the [GNU General Public License](http://www.gnu.org/licenses/gpl-2.0.txt) as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

The content is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

## Quick Start

*   The application depends on [Tst](https://github.com/gcrossland/Tst). Prepare to use this first.
*   Ensure that the contents of [libraries](../libraries) is available on PYTHONPATH e.g. `export PYTHONPATH=/path/to/TransparentBackup/libraries:${PYTHONPATH}`.
*   Run the tests by running [Tst](https://github.com/gcrossland/Tst)'s runtsts.py utility from the working directory (or archive) root.
*   Run Transparent Backup by invoking Python with the path to the working directory (or archive) root (or with \_\_main\_\_.py).
    ```shell
    python /path/to/TransparentBackup --backup-source /dir/to/backup --output /dir/for/output0 --scripttype BashScript
    python /path/to/TransparentBackup --backup-source /dir/to/backup --diff-dtml /dir/for/output0/\!fullstate.dtml --output /dir/for/output1 --scripttype BashScript
    ```
*   The application also comes with the utility makebackups.py, which is a wrapper for Transparent Backup that automatically compiles the snapshots, preserves DTML files describing those snapshots in the current directory and uses those DTML files to make subsequent backup runs incremental.
    ```shell
    /path/to/TransparentBackup/makebackups.py /dir/for/snapshots Bash /dir/to/backupA /dir/to/backupB
    ```
