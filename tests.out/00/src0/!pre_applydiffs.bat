chcp 1252
REM Prepares the previous state of the backup set, rooted in the current directory, for having new files copied over it
MKDIR ".\A Subdirectory"
MKDIR ".\Deleted Subdirectory"
MKDIR ".\Moved Subdirectory"
REM Transfers copied files to temporary dirs
REM Transfers copied files to final destination
REM Clears away deleted objects and temporary dirs
