chcp 1252
REM Converts the aggregation of the previous state of the backup set and the updated files, rooted in the current directory, to the final new state
REM Copies duplicated updated files to all destinations
COPY ".\Created File.txt" ".\New Moved Subdirectory\Created File.txt"
